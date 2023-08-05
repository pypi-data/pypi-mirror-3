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
from time             import time
from coils.core       import *
from process          import Process as WFProcess
import multiprocessing

def start_workflow_process(p, c):
    w = WFProcess(p, c)
    w.run()


class ExecutorService(Service):
    __service__ = 'coils.workflow.executor'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._workers = { }
        self.send(Packet('coils.workflow.executor/ticktock',
                         'coils.clock/subscribe',
                         None))
        self._pending = { }

    def _start_a_queued_process(self):
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.manager/checkQueue:{0}'.format(len(self._workers)),
                         None))

    def _start_process(self, process_id):
        self.log.debug('Requesting properties for processId#{0}'.format(process_id))
        uuid = self.send(Packet('coils.workflow.executor/__null',
                                'coils.workflow.manager/get_properties:{0}'.format(process_id),
                                None),
                         callback = self._start_callback)
        self.log.debug('property request packet is {0}'.format(uuid))
        self._pending[uuid] = int(process_id)

    def _start_callback(self, uuid, source, target, data):
        process_id = data.get('process_id', None)
        if (process_id is None):
            self.log.error('Received request to start a NULL processId!')
            return True
        self.log.debug('Received properties for processId#{0}'.format(process_id))

        import pprint
        self.log.debug('pending: {0}'.format(pprint.pformat(self._pending)))
        self.log.debug('workers: {0}'.format(pprint.pformat(self._workers)))

        if (uuid in self._pending):
            # TODO: Verify this UUID corresponds to the process we expected

            # We may have multiple requests for this processes properties outstanding,
            # so once we have one we want to discard all the remaining once so we
            # don't bother to do this again
            self.send(Packet('coils.workflow.executor/__null',
                             'coils.workflow.logger/log',
                             { 'process_id': process_id,
                               'category': 'debug',
                               'message': 'Received OIE properties'}))
            pending = { }
            for x in self._pending.items():
                if (x[1] != process_id):
                    pending[x[0]] = x[1]
                    self.log.debug('Discarding duplicate request for process properties, request saited.')
            self._pending = pending
            self.log.debug('reduced pending: {0}'.format(pprint.pformat(self._pending)))

            start = True # assume we are going to start
            if (data['properties'].get('singleton', '').upper() == 'YES'):
                for pid in self._workers:
                    worker = self._workers[pid]
                    if ((worker['route_group'] == data['route_group'].lower()) and
                        (worker['status'] == 'running')):
                        self.send(Packet('coils.workflow.executor/__null',
                                         'coils.workflow.logger/log',
                                         { 'process_id': process_id,
                                           'category': 'control',
                                           'message': 'processId#{0} belongs to singleton route group "{1}" and cannot be started due to processId#{2}'.\
                                                format(process_id, data['route_group'], pid) } ) )
                        self.log.info('Requesting processId#{0} be placed in a queued state'.format(process_id))
                        self.send(Packet('coils.workflow.executor/__null',
                                         'coils.workflow.manager/queue:{0}'.format(process_id),
                                  None))
                        start = False # cancel start
                        break
            if (start):
                self._create_worker(process_id, context_id = int(data['context_id']),
                                                route_group = data['route_group'],
                                                route_id = int(data['route_id']))
        else:
            self.log.debug('Received properties for non-pending processId#{0}'.format(data['process_id']))
        return True

    def _create_worker(self, process_id, context_id=None, route_group=None, route_id=None):
        self.log.debug('Attempting to start/restart processId#{0}'.format(process_id))
        if (process_id in self._workers):
            # TODO: Signal the route, maybe it wants to check for new messages?
            self.log.info('Request to create worker for already running processId#{0}'.format(process_id))
        else:
            self.send(Packet('coils.workflow.executor/__null',
                             'coils.workflow.logger/log',
                             { 'process_id': process_id,
                               'category': 'debug',
                               'message': 'Creating worker.'} ))
            # Start a new process
            s, r = multiprocessing.Pipe()
            p = multiprocessing.Process(target=start_workflow_process,
                                        args=(process_id, context_id))
            self._workers[process_id] = { 'process_id': process_id,
                                          'route_id':   route_id,
                                          'status':     'running',
                                          'timestamp':   time(),
                                          'route_group': route_group.lower(),
                                          'context_id':  context_id,
                                          'process':     p }
            try:
                p.start()
                p.join(0.2)
            except Exception, e:
                self.log.error('Failed to create worker for processId#{0}'.format(process_id))
                self.log.exception(e)
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.logger/log',
                                 { 'process_id': process_id,
                                   'category': 'error',
                                   'message': 'Worker creation failed.'} ))
                del self._workers[process_id]
            else:
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.logger/log',
                                 { 'process_id': process_id,
                                   'category': 'debug',
                                   'message': 'Worker started.'} ))
                self.log.debug('Worker for processId#{0} started.'.format(process_id))

    def _restart_process(self, process_id):
        if (process_id in self._workers):
            # TODO: Signal the route, maybe it wants to check for new messages?
            self.log.info('Received start signal for already running process.')
            return
        else:
            self._start_process(process_id)

    def do_start(self, parameter, packet):
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Request to start.'} ))
        self.log.info('Received message to start/restart processId#{0}'.format(process_id))
        try:
            self._start_process(process_id)
        except Exception, e:
            self.log.warn('Unable to start procesId#{0}'.format(process_id))
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'ERROR'}))
        else:
            self.log.info('Successfully started processId#{0}'.format(process_id))
            self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))

    def do_signal(self, parameter, packet):
        # TODO: Authorize signal!
        try:
            process_id = packet.data.get('processId')
            self._restart_process(process_id)
        except Exception, e:
            self.send(Packet.Reply(packet, { 'status': 500,
                                             'text': '{0}'.format(e) } ) )
        else:
            self.send(Packet.Reply(packet, { 'status': 201,
                                             'text': 'OK' } ) )

    def do_running(self, parameter, packet):
        ''' Packet indicates the process is actively working, update the timestamp '''
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Process reported as running.'} ))
        if (process_id in self._workers):
            worker = self._workers.get(process_id)
            if (worker.get('timestamp') < packet.time):
                self._workers[process_id]['status'] = 'running'
                self._workers[process_id]['timestamp'] = time()
        else:
            self.log.info('Learned of unknown worker for processId#{0}'.format(process_id))
            self._workers[process_id] = { 'process_id': process_id,
                                          'route_id':   None,
                                          'status':     'running',
                                          'timestamp':   time(),
                                          'route_group': str(process_id),
                                          'context_id':  0,
                                          'process':     None }

    def do_parked(self, parameter, packet):
        ''' Parking a workflow is effectively the same as shutting down.'''
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Process reported as parked.'} ))
        if (process_id in self._workers):
            #del self._workers[process_id]
            self._workers[process_id]['status'] = 'parked'
            self.log.debug('discarding parked process {0}'.format(process_id))
        return

    def do_failure(self, parameter, packet):
        ''' When a process fails shut down the worker '''
        # TODO: Send an administrative notice?
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Process reported as failed.'} ))
        if (process_id in self._workers):
            #del self._workers[process_id]
            self._workers[process_id]['status'] = 'failed'
        if (len(self._workers) < 10):
            self._start_a_queued_process()
        return

    def do_complete(self, parameter, packet):
        ''' When a process is complete, shut down the worker '''
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Process reported as completed.'} ))
        if (process_id in self._workers):
            #del self._workers[process_id]
            self._workers[process_id]['status'] = 'complete'
            self.log.debug('discarding completed process {0}'.format(process_id))
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.reaper/deleteProcess:{0}'.format(process_id),
                         None))
        self._start_a_queued_process()

    def do_ticktock(self, parameter, packet):
        self.log.info('TickTock: {0} active workers'.format(len(self._workers)))
        if len(self._workers):
            self.send(Packet('coils.workflow.executor/__null',
                            'coils.workflow.executor/verify_workers',
                            None ))
        self._start_a_queued_process()

    def do_is_running(self, parameter, packet):
        process_id = int(parameter)
        self.log.info('Process status check for processId#{0} by {1}'.format(process_id, packet.source))
        if (process_id in self._workers):
            if (self._workers[process_id]['process'] is None):
                # Worker is not one of our children, we can only assume it is alive, this may occur
                # if an executor with children dies or is killed and the component is restarted. The
                # new executor may learn of the children as then send do_running signals;  but we will
                # never again have their process object.
                self.send(Packet.Reply(packet, { 'status': 200,
                                                 'text': 'OK; no entry',
                                                 'running': 'NO',
                                                 'process_id': process_id } ) )
            else:
                # Worker is one of our children, we can verify its life
                self._workers[process_id]['process'].join(0.1)
                if (self._workers[process_id]['process'].is_alive()):
                    self.send(Packet.Reply(packet, { 'status': 200,
                                                     'text': 'OK; running',
                                                     'running': 'YES',
                                                     'processId': process_id } ) )
                else:
                    self.send(Packet.Reply(packet, { 'status': 200,
                                                     'text': 'OK; no worker',
                                                     'running': 'NO',
                                                     'processId': process_id  } ) )
                    self.log.info('Discarding worker for processId#{0}'.format(process_id))
                    del self._workers[process_id]
        else:
            self.log.info('No worker found for processId#{0}'.format(process_id))
            self.send(Packet.Reply(packet, { 'status': 200,
                                             'text': 'OK; no entry',
                                             'running': 'NO',
                                             'process_id': process_id } ) )

    def do_kill(self, parameter, packet):
        process_id = int(parameter)
        signal = packet.data.get('signal', 15)
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'control',
                           'message': 'Request to kill.'} ))
        if (process_id in self._workers):
            if (signal == 9):
                # hard kill
                # TODO: implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            elif (signal == 15):
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.process.{0}/kill:{0}'.format(process_id),
                                 None))
                self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
            elif (signal == 1):
                # Reload ?
                # TODO Implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            elif (signal == 17):
                # Suspend (Park!)
                # TODO Implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            else:
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Unknown kill signal'}))
        else:
            self.send(Packet.Reply(packet, {'status': 404, 'text': 'OK', 'running': 'No worker for PID' }))

    def do_verify_workers(self, parameter, packet):
        purge = [ ]
        self.log.info('Worker status verification requested by {0}'.format(packet.source))
        for pid in self._workers:
            self.log.info('Verifying worker for processId#{0}'.format(pid))
            if (self._workers[pid]['process'] is None):
                continue
            self._workers[pid]['process'].join(0.1)
            if (self._workers[pid]['process'].is_alive()):
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.logger/log',
                                 { 'process_id': pid,
                                   'category': 'control',
                                   'message': 'Verified life of worker'}))
            else:
                self.log.info('Worker for processId#{0} is defunct in state {1}'.format(pid, self._workers[pid]['status']))
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.logger/log',
                                 { 'process_id': pid,
                                   'category': 'control',
                                   'message': 'Detected defunct worker with state "{0}"'.format(self._workers[pid]['status'])}))
                if (self._workers[pid]['status'] != 'started'):
                    purge.append(pid)
                else:
                    # TODO: Can we do something about it?
                    pass
        self.log.info('Workder verification complete')
        if (len(purge) > 0):
            for pid in purge:
                self.log.info('Discarding worker for processId#{0}'.format(pid))
                del self._workers[pid]
                 # TODO: Prove more information about the defunct process
                self.send(Packet('coils.workflow.executor/__null',
                                  'coils.workflow.manager/failed:{0}'.format(pid),
                                  None))
