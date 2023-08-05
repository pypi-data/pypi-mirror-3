#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import filename_for_process_markup

class GetProcess(GetCommand):
    __domain__ = "process"
    __operation__ = "get"

    def set_markup(self, processes):
        for process in processes:
            handle = BLOBManager.Open(filename_for_process_markup(process), 'rb', encoding='binary')
            if (handle is not None):
                bpml = handle.read()
                process.set_markup(bpml)
                BLOBManager.Close(handle)
            else:
                self.log.error('Found no process markup for processId#{0}'.format(process.object_id))
        return processes

    def run(self, **params):
        db = self._ctx.db_session()
        if (self.query_by == 'object_id'):
            if (len(self.object_ids) > 0):
                query = db.query(Process).filter(and_(Process.object_id.in_(self.object_ids),
                                                       Process.status != 'archived'))
        else:
            self.set_multiple_result_mode()
            query = db.query(Process).filter(and_(Process.owner_id.in_(self._ctx.context_ids),
                                                   Process.status != 'archived'))
        self.set_return_value(self.set_markup(query.all()))
        