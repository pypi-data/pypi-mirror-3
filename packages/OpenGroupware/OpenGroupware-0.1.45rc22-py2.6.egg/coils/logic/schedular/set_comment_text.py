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
from datetime           import datetime, timedelta
from pytz               import timezone
from sqlalchemy         import *
from sqlalchemy.orm     import *
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand

class SetComment(CreateCommand):
    __domain__ = "appointment"
    __operation__ = "set-comment-text"

    def __init__(self):
        Command.__init__(self)

    def prepare(self, ctx, **params):
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('appointment' in params):
            self.parent_id = int(params['appointment'].object_id)
        elif ('parent_id' in params):
            self.parent_id = int(params['parent_id'])
        elif ('parent_id' in self.values):
            self.parent_id = int(self.values['parent_id'])
        else:
            raise CoilsException('')
        if ('text' in params):
            self.text = params['text']
        elif ('appointment' in params):
            self.text = params['appointment'].get_comment()

    def run(self):
        db = self._ctx.db_session()
        self.obj = db.query(DateInfo).filter(DateInfo.parent_id==self.parent_id).first()
        if (self.obj is not None):
            # Update
            self.obj.text = self.text
        else:
            # Create
            self.obj = DateInfo(self.parent_id, text=self.text)
            self.set_object_id()
            self.save()
        self._result = self.obj.text
