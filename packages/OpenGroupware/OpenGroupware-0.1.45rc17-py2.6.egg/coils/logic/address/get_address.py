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
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand

class GetAddress(GetCommand):
    __domain__ = "address"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (len(self.object_ids) == 0):
            if ('parent_id' in params):
                self.parent_id = int (params.get('parent_id'))
                if ('kind' in params):
                    self.mode = 1
                    self.kind = params.get('kind')
                else:
                    self.kind = None
                    self.mode = 2

    def run(self, **params):
        self.access_check = False
        db = self._ctx.db_session()
        if (len(self.object_ids) > 0):
            query = db.query(Address).filter(and_(Address.object_id.in_(self.object_ids),
                                                   Address.status != 'archived'))
        else:
            if (self.kind is None):
                query = db.query(Address).filter(and_(Address.parent_id==self.parent_id,
                                                         Address.status != 'archived'))
            else:
                query = db.query(Address).filter(and_(Address.parent_id==self.parent_id,
                                                         Address.kind==self.kind,
                                                         Address.status != 'archived'))

        self.set_return_value(query.all())
