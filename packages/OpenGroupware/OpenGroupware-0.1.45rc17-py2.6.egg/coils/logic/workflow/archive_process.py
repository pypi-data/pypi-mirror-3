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
import pickle, yaml
from sqlalchemy                   import *
from coils.core                   import *
from coils.foundation             import Route, Process, Message
from coils.logic.workflow.formats import Format

class ArchiveProcess(Command):
    __domain__ = "process"
    __operation__ = "archive"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('process' in params):
            self._process = params.get('process').object_id
        elif ('pid' in params):
            self._process = self._ctx.run_command('process::get', id=int(params.get('pid')))
        else:
            raise CoilsException('Request to archive process with no PID')

    def run(self):
        # Delete Messages
        messages = []
        for message in db.query(Message).filter(Message.process_id == self.pid).all():
            messages.append(message.uuid)
        for uuid in messages:
            self._ctx.run_command('message::delete', uuid=uuid)
        for 
