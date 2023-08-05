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

class ReaperService(Service):
    __service__ = 'coils.workflow.reaper'
    __auto_dispatch__ = True
    __is_worker__     = True
    __TimeOut__       = 60

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._pids = []
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._pm = self._ctx.property_manager

    def work(self):
        self.log.debug('{0} processes scheduled for reap.'.format(len(self._pids)))
        while (len(self._pids) > 0):
            pid = self._pids.pop()
            self._delete_process(pid)
            self._ctx.commit()

    def _delete_process(self, pid):
        delete = True
        process = self._ctx.run_command('process::get', id=pid)
        if (process is not None):
            x = self._pm.get_property(process.route_id,
                                      'http://www.opengroupware.us/oie',
                                      'preserveAfterCompletion')
            if (x is not None):
                self.log.info('Found preserveAfterCompletion property on route, value is {0}'.\
                    format(str(x.get_value())))
                if (str(x.get_value()).upper() == 'YES'):
                    self.send(Packet(None,
                                     'coils.workflow.logger/log',
                                     { 'process_id': pid,
                                       'message': 'Not deleting process, route property indicates preservation' } ) )
                    delete = False
            if (delete):
                self.log.debug('Deleting data for completed process {0}'.format(pid))
                self._ctx.run_command('process::delete', id=pid)
                self.send(Packet(None,
                                 'coils.workflow.logger/reap:{0}'.format(pid),
                                 None))
            else:
                self.log.debug('Deletion of processId#{0} supressed.'.format(pid))
        return delete

    def do_deleteprocess(self, parameter, packet):
        pid = int(parameter)
        self._pids.append(parameter)
        self.log.info('deletion of data for processId#{0} requested'.format(pid))
        self.send(Packet.Reply(packet, {'STATUS': 201, 'MESSAGE': 'OK'}))
        return

