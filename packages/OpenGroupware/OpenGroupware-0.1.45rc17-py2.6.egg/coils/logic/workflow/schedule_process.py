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

class ScheduleProcess(Command):
    __domain__ = "process"
    __operation__ = "schedule"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._data = { }
        self._data['uuid']      = params.get('uuid', None)
        self._data['contextId'] = params.get('context_id', self._ctx.account_id)
        self._data['priority']  = int(params.get('priority', 175))
        self._data['inputData'] = params.get('input_data', None)
        self._callback = params.get('callback', None)
        #
        # Route
        #
        if ('route' in params):
            self._route = params.get('route')
        elif ('route_id' in params):
            route_id = int(params.get('route_id'))
            self._route = self._ctx.run_command('route::get', id=route_id )
            if (self._route is None):
                raise CoilsException('Unable to access route {0} to schedule process'.format(route_id))
        else:
            raise CoilsException('No route specified for scheduled process.')
        #
        # Get schedule parameters
        #
        if ('date' in params):
            #TODO: Test date is within one year
            self._data['date']    = params.get('date')
        elif (('start' in params) or ('repeat' in params)):
            # Interval
            self._data['weeks']   = int(params.get('weeks', 0))
            self._data['days']    = int(params.get('days', 0))
            self._data['hours']   = int(params.get('hours', 0))
            self._data['minutes'] = int(params.get('minutes', 0))
            self._data['seconds'] = int(params.get('seconds', 0))
            self._data['start']   = params.get('start', datetime.now())
            self._data['repeat']  = int(params.get('repeat', 1))
        else:
            # Crontab
            self._data['year']    = str(params.get('year', '*'))
            self._data['month']   = str(params.get('month', '*'))
            self._data['day']     = str(params.get('day', '*'))
            self._data['weekday'] = str(params.get('weekday', '*'))
            self._data['hour']    = str(params.get('hour', '*'))
            self._data['minute']  = str(params.get('minute', '*'))

    def run(self):
        self._result = False
        target = 'coils.workflow.scheduler/schedule_job:{0}'.format(self._route.object_id)
        self._result = self._ctx.send(None,
                                      target,
                                      self._data,
                                      callback=self._callback)
