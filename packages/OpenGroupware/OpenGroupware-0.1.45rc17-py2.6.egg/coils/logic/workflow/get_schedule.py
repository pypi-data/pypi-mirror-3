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

class GetProcessSchdule(Command):
    __domain__ = "process"
    __operation__ = "get-schedule"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._route_id = None
        self._all_jobs = False
        if ('all_jobs' in params):
            self._all_jobs  = bool(params.get('all_jobs'))
        elif ('route' in params):
            self._route_id = params.get('route').object_id
        elif ('route_id' in params):
            self._route_id = int(params.get('route_id'))
        self._callback  = params.get('callback', None)

    def run(self):
        self._result = False
        source = None # TODO: How to set?
        if ((self._all_jobs) or (self._route_id is not None)):
            if (self._ctx.is_admin):
                if (self._all_jobs):
                    target = 'coils.workflow.scheduler/list_jobs'
                else:
                    target = 'coils.workflow.scheduler/list_jobs:{0}'.format(self._route_id)
            else:
                raise CoilsException('Listing schedule requires administrative role')
        else:
            target = 'coils.workflow.scheduler/list_my_jobs:{0}'.format(self._ctx.account_id)
        self._result = self._ctx.send(None,
                                      target,
                                      None,
                                      callback=self._callback)
