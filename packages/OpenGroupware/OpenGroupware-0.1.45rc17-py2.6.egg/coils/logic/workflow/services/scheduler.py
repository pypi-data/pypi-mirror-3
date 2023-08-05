#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
import pickle, logging, traceback
from collections           import deque
from cron_thread           import CronThread
from coils.core            import *


class SchedulerService(Service):
    # TODO: Issue#63 - Deleted routes should be removed from schedule
    __service__ = 'coils.workflow.scheduler'
    __auto_dispatch__ = True
    __TimeOut__        = 60
    __DebugOn__       = None

    def __init__(self):
        self._ctx      = AdministrativeContext()
        self._queue      = deque()
        Service.__init__(self)
        if (SchedulerService.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            SchedulerService.__DebugOn__ = sd.bool_for_default('OIESchedulerDebugEnabled')

    @property
    def debug(self):
        return SchedulerService.__DebugOn__

    #
    # Run Queue Management
    #

    def _queue_process(self, uuid, route_id, context_id, input_data, kwargs=None):
        self.log.info('Queued entry {0} [routeId#{1} contextId#{2} for execution'.format(uuid, route_id, context_id))
        self._queue.append((uuid, route_id, context_id, input_data))

    def _run_queue(self):
        if (self.debug):
            self.log.debug('Checking run_queue.')
        if (len(self._queue) > 0):
            self.log.debug('Have jobs in run queue.')
            run_queue = [ ]
            try:
                while True:
                    job = self._queue.pop()
                    run_queue.append(job)
            except IndexError:
                try:
                    self.schedular.save_schedule()
                except Exception, e:
                    # TODO: Catch specific types of exceptions
                    self.log.exception(e)
                    message =  traceback.format_exc()
                    message = 'Workflow process message log cannot be flushed to database.\n{0}'.format(message)
                    self.send_administrative_notice(
                        category='workflow',
                        urgency=9,
                        subject='Unable to update scheduled workflows',
                        message=message)
                else:
                    if (self.debug):
                        self.log.debug('Found {0} jobs in run queue'.format(len(run_queue)))
                    for uuid, route_name, context_id, input_data in run_queue:
                        self._start_process(uuid, route_name, context_id, input_data)

    def _start_process(self, uuid, route_id, context_id, input_data, kwargs=None):
        ctx = AssumedContext(context_id, broker=self._broker)
        self.log.info('Attempting to start scheduled job {0}'.format(uuid))
        if (input_data is None):
            input_data = u''
        try:
            route = ctx.run_command('route::get', id=route_id)
            if (route is not None):
                try:
                    process = ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                       'data':     input_data,
                                                                       'priority': 200 })
                except Exception, e:
                    # TODO: Add administrative notification of failure to create process
                    self.log.error('Unable to create scheduled process; route "{0}" in contextId#{1}'.\
                                   format(route_name, context_id))
                    self.log.exception(e)
                else:
                    try:
                        process = ctx.run_command('process::start', process=process)
                        self.log.error('Start of processId#{0} requested'.format(process.object_id))
                    except Exception, e:
                        # TODO: Add administrative notification of failure to start process
                        self.log.error('Unable to request process start for objectId#{0}'.\
                                       format(process.object_id))
                        self.log.exception(e)
                    finally:
                        ctx.commit()
            else:
                message = "Scheduling indicates that a process should be created " \
                          "but the specified route could not be found.\n" \
                          " RouteId#{0}\n" \
                          " ContextId#{1}\n" \
                          " UUID:{2}\n" \
                          " Length of Input Message: {3}\n".format(route_id,
                                                                   context_id,
                                                                   uuid,
                                                                   len(input_data))
                self.send_administrative_notice(subject="Route not available to create scheduled process",
                                                message=message,
                                                urgency=8,
                                                category='workflow')
                self.log.error('Unable to load routeID#{0} to create process'.format(route_id))
        except Exception, e:
            self.log.exception(e)
        finally:
            ctx.close()

    #
    # Plumbing
    #

    def prepare(self):
        Service.prepare(self)
        # Statup the APSchedular
        try:
            self.log.debug('Creating CRON thread.')
            self.schedular = CronThread(self)
            #self.schedular.configure(misfire_grace_time=10)
            self.log.debug('Starting CRON thread.')
            self.schedular.start()
        except Exception, e:
            self.log.exception(e)
            raise e
        else:
            self.log.info('CRON thread started.')

    def shutdown(self):
        # We override Service.shutdown so we can tell the APSchedular to shutdown
        self.schedular.shutdown(10)
        Service.shutdown(self)

    def work(self):
        self._run_queue()

    #
    # RPC methods
    #

    def do_list_jobs(self, route, packet):
        self.send(Packet.Reply(packet, { u'status':   200,
                                         u'schedule': self.schedular.list_jobs() } ) )

    def do_list_my_jobs(self, context_id, packet):
        context_id = int(context_id)
        self.send(Packet.Reply(packet, { u'status':   200,
                                         u'schedule': self.schedular.list_all_jobs_for_context(context_id) } ) )

    def do_schedule_job(self, route_id, packet):
        try:
            route_id   = int(route_id)
            context_id = int (packet.data.get('contextId'))
            if ('date' in packet.data):
                # Date job
                if (self.debug):
                    self.log.debug('Scheduling date job')
                self.schedular.add_date_job(self._queue_process,
                                            packet.data.get('date'),
                                            args=(packet.uuid,
                                                  route_id,
                                                  context_id,
                                                  packet.data.get('inputData', None)))
            elif (('start' in packet.data) or ('repeat' in packet.data)):
                # Interval
                if (self.debug):
                    self.log.debug('Scheduling interval job')
                self.schedular.add_interval_job(self._queue_process,
                                                weeks=int(packet.data.get('weeks', 0)),
                                                days=int(packet.data.get('days', 0)),
                                                hours=int(packet.data.get('hours', 0)),
                                                minutes=int(packet.data.get('minutes', 0)),
                                                seconds=int(packet.data.get('seconds', 0)),
                                                start_date=packet.data.get('start', None),
                                                repeat=int(packet.data.get('repeat', 0)),
                                                args=(packet.uuid,
                                                      route_id,
                                                      context_id,
                                                      packet.data.get('inputData', None)))
            else:
                # Crontab style
                if (self.debug):
                    self.log.debug('Scheduling chronological job')
                self.schedular.add_cron_job(self._queue_process,
                                            year=str(packet.data.get('year', '*')),
                                            month=str(packet.data.get('month', '*')),
                                            day=str(packet.data.get('day', '*')),
                                            day_of_week=str(packet.data.get('weekday', '*')),
                                            hour=str(packet.data.get('hour', '*')),
                                            minute=str(packet.data.get('minute', '*')),
                                            args=(packet.uuid,
                                                  route_id,
                                                  context_id,
                                                  packet.data.get('inputData', None)))
        except Exception, e:
            self.log.exception(e)
            self.send(Packet.Reply(packet, { u'status': 500,
                                             u'text': unicode(e),
                                             u'uuid': None}))
        else:
            self.send(Packet.Reply(packet, { u'status': 200,
                                             u'text': 'Process scheduled OK',
                                             u'uuid': packet.uuid}))

    def do_unschedule_job(self, uuid, packet):
        if (self.schedular.cancel_job_by_uuid(uuid, [int(x) for x in packet.data.get('contextIds', [])])):
            self.send(Packet.Reply(packet, { u'status': 200,
                                             u'uuid': uuid,
                                             u'text': 'Job cancelled.' } ) )
        else:
            self.send(Packet.Reply(packet, { u'status': 404,
                                             u'uuid': uuid,
                                             u'text': u'No such job' } ) )
