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
from datetime           import datetime
from sqlalchemy         import *
from coils.core         import *

class UnscheduleProcess(Command):
    __domain__ = "process"
    __operation__ = "unschedule"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._uuid = params.get('uuid', None)
        self._callback = params.get('callback', None)
        if (self._uuid is None):
            raise CoilsException('Request to cancel scheduled process with no scheduled process id')

    def run(self):
        self._result = False
        source = None # TODO: How to set?
        target = 'coils.workflow.scheduler/unschedule_job:{0}'.format(self._uuid)
        self._result = self._ctx.send(None,
                                      target,
                                      { 'contextIds': [int(x) for x in self._ctx.context_ids] },
                                      callback=self._callback)

