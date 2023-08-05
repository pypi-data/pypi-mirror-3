#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from uuid               import uuid4
from sqlalchemy         import and_
from time               import time
from StringIO           import StringIO
from coils.core         import *
from coils.logic.workflow.utility import filename_for_process_log, \
                               read_cached_process_log, \
                               delete_cached_process_logs, \
                               cache_process_log


class LoggerService(Service):
    __service__ = 'coils.workflow.logger'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._log_queue = BLOBManager.OpenShelf(uuid='coils.workflow.logger')
        self.send(Packet('coils.workflow.logger/ticktock',
                         'coils.clock/subscribe',
                         None))        

    def _log_message(self, source, process_id, message, stanza=None,
                                                        timestamp=None,
                                                        category='undefined',
                                                        uuid=None):
        try:
            if (timestamp is None):
                timestamp = float(time())                                                            
            self._log_queue[uuid4().hex] = (source, process_id, message.strip(), stanza, timestamp, category, uuid)
            self._log_queue.sync()
        except Exception, e:
            self.log.exception(e)
            return False
        else:
            return True

    def _empty_queue(self):
        keys = [ ]
        try:
            
            for key in self._log_queue:
                source, process_id, message, stanza, timestamp, category, uuid = self._log_queue[key]
                entry = ProcessLogEntry(source,
                                        process_id,
                                        message,
                                        stanza    = stanza,
                                        timestamp = timestamp,
                                        category  = category,
                                        uuid      = uuid)
                self._ctx.db_session().add(entry)
                keys.append(key)
        except Exception, e:
            message = 'Workflow process message log cannot be flushed to database.\n{0}'.format(traceback.format_exc())
            subject = 'Exception creating process log entry!'
            self.log.error(subject)
            self.log.exception(e)
            self.send_administrative_notice(subject=subject,
                                            message=message,
                                            urgency=9,
                                            category='workflow')
        else:
            try:
                self.log.debug('Commiting {0} process log entries'.format(len(keys)))
                self._ctx.commit()
            except Exception, e:
                # TODO: Send an administrative notice!
                self.log.exception(e)
            else:
                for key in keys:
                    del self._log_queue[key]
            self._log_queue.sync()
            self.log.debug('{0} process log entries purged from queue'.format(len(keys)))        

    def do_ticktock(self, parameter, packet):
        self._empty_queue()

    def do_log(self, parameter, packet):
        try:
            source     = Packet.Service(packet.source)
            process_id = int(packet.data.get('process_id'))
            message    = packet.data.get('message', None)
            stanza     = packet.data.get('stanza', None)
            category   = packet.data.get('category', 'undefined')
            uuid       = packet.uuid
            timestamp  = packet.time
        except Exception, e:
            self.log.exception(e)
            self._ctx.rollback()
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to parse packet payload.'}))
        else:
            if (self._log_message(source, process_id, message, stanza=stanza,
                                                               timestamp=timestamp,
                                                               category=category,
                                                               uuid=uuid)):
                self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
            else:
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to record message.'}))

    def do_get_log(self, parameter, packet):
        # TODO: Support HTML & XML formats for response
        try:
            source     = Packet.Service(packet.source)
            process_id = int(parameter)
            format     = packet.data.get('format', 'text/plain')
            uuid       = packet.uuid
        except Exception, e:
            self.log.exception(e)
            self._ctx.rollback()
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to parse packet payload.'}))
            return

        process = self._ctx.run_command('process::get', id=process_id, access_check=False)
        self.log.debug('Process: {0}'.format(process))
        if process:
            self.log.debug('got process object')
            # Attempt to read the log from the cache'd process logs
            log_text = read_cached_process_log(process.object_id, process.version)
        else:
            # Eh? There is no such process
            self.log.debug('no such process as {0}'.format(process_id))
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'No such process as objectId#{0}'.format(process_id)}))
            return

        db = self._ctx.db_session()
        if not log_text:
            # Process log text is not cached for this version, we need to build one
            self.log.debug('generating log')
            self._empty_queue()

            query = db.query(ProcessLogEntry).\
                        filter(and_(ProcessLogEntry.process_id == process_id,
                                     ProcessLogEntry.stanza != None)).\
                        order_by(ProcessLogEntry.timestamp)
            logs = query.all()
            content = StringIO(u'')
            stanza = None
            start  = None
            for log in logs:
                if stanza != log.stanza:
                    if (stanza is not None):
                        content.write(u'\n')
                    stanza = log.stanza
                    content.write(u'Stanza {0}\n'.format(stanza.strip()))
                category = log.category
                if (category is None):
                    category = 'info'
                else:
                    category = category.strip()
                    if (category == 'start'):
                        start = log.timestamp
                content.write('{0}:{1}\n'.format(category.strip(), log.message))
                if ((category == 'complete') and (start is not None)):
                    content.write('duration:{0}s\n'.format(log.timestamp - start))
                    start = None
            log_text = content.getvalue()
            content.close()
            content = None
            cache_process_log(process.object_id, process.version, log_text)

        self.send(Packet.Reply(packet, { 'status': 200,
                                         'text': 'OK',
                                         'payload': { 'text': log_text, 'version': process.version } } ) )
        db.rollback()

    def do_reap(self, parameter, packet):
        process_id = int(parameter)
        db = self._ctx.db_session()
        try:
            db.query(ProcessLogEntry).\
                filter(ProcessLogEntry.process_id == process_id).\
                delete(synchronize_session='fetch')
        except Exception, e:
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to purge process log.'}))
        else:
            self._ctx.commit()
            self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
