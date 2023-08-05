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
from time import time
from sqlalchemy         import *
from coils.core         import *

class GetProcessLog(Command):
    __domain__ = "process"
    __operation__ = "get-log"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._obj = params.get('process', params.get('object', None))
        if (self._obj is None):
            self._pid = params.get('pid', params.get('id', None))
        else:
            self._pid = self._obj.object_id
        self._callback = params.get('callback', None)
        self._format   = params.get('format', 'text/plain')
        if (self._pid is None):
            raise CoilsException('ProcessId required to retreive process OIE proprties')

    def _local_callback(self, uuid, source, target, data):
        self.log.debug('process:get-log self callback reached.')
        if data:
            if isinstance(data, dict):
                status = data.get('status', 500)
                self.log.debug('process logger component responded with status {0}'.format(status))
                if (status == 200):
                    # TODO: READ FROM ATTACHMENT
                    self._log_text = data['payload']['text']
                    # TODO: DELETE ATTACHMENT
                else:
                    raise CoilsException('Logger reports error returning process log.')
            else:
                raise CoilsException('Unexpected data type in packet payload from logger.')
        else:
            raise CoilsException('Logger responded with packet having no payload.')
        return True


    def _wait(self):
        if (self._log_text is None):
            if (time() < self._timeout):
                return True
        return False

    def run(self):
        # If no callback was provided process::get-log will try to behave as a syncronous
        # commmand; it will register its own callback and wait a "reasonable" amount
        # of time for the response from the logger component.
        # WARN: This command in self-callback mode issues a wait() so other callbacks could
        #       get called while the context is waiting for the response.
        self._log_text = None
        if (self._callback is None):
            self._callback = self._local_callback
            local_callback = True
            self.log.debug('process::get-log using self callback')
        else:
            local_callback = False
        self._ctx.send(None, 'coils.workflow.logger/get_log:{0}'.format(self._pid),
                             { 'format': self._format },
                             callback = self._callback)
        if (local_callback):
            self._timeout = time() + 10
            self.log.debug('entering wait @ {0} till {1}'.format(time(), self._timeout))
            while (self._wait()):
                self._ctx.wait(timeout=10000)
                self.log.debug('resuming wait @ {0}'.format(time()))
            self.log.debug('exited wait @ {0}'.format(time()))
            if (self._log_text is None):
                raise CoilsException('No response from coils.workflow.logger')
            else:
                self._result = self._log_text
        else:
            self._result = self._uuid


