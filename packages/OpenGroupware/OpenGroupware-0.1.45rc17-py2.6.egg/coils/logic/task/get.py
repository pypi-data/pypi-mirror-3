#!/usr/bin/python
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
# THE SOFTWARE.
#
from sqlalchemy       import *
from coils.foundation import *
from coils.core       import *
from coils.core.logic import *

class GetTask(GetCommand):
    __domain__ = "task"
    __operation__ = "get"

    def parse_parameters(self, **params):
        self.obj         = None
        self._caldav_uid = None
        GetCommand.parse_parameters(self, **params)
        if (len(self.object_ids) == 0):
            if ('uid' in params):
                self._caldav_uid = unicode(params.get('uid'))
                self.mode = RETRIEVAL_MODE_SINGLE

    def run(self, **params):
        db = self._ctx.db_session()

        #query = db.query(Task).filter(and_(Task.object_id.in_(self.object_ids),
        #                                    Task.status != 'archived'))
        #data = query.all()
        #if (self.access_check):
        #    data = self._ctx.access_manager.filter_by_access(self._ctx, 'r', data)
        #self.set_return_value(query.all())

        if (self._caldav_uid is None):
            query = db.query(Task).filter(and_(Task.object_id.in_(self.object_ids),
                                                Task.status != 'archived'))
        else:
            query = db.query(Task).filter(and_(Task.status != 'archived',
                                                Task.caldav_uid == self._caldav_uid))
        self.set_return_value(query.all())
