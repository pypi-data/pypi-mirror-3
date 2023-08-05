#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand
from keymap             import COILS_DOCUMENT_KEYMAP

class AttachToObject(Command):
    __domain__    = "object"
    __operation__ = "attach"

    def prepare(self, ctx, **params):
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self._object      = params.get('object', None)
        self._payload     = params.get('payload', None)
        self._name        = params.get('name')
        self._mimetype    = params.get('mimetype', 'application/octet-stream')

    def run(self):
        folder_name = 'attachContainer:{0}'.format(self._object.object_id)
        db = self._ctx.db_session()
        query = db.query(Folder).filter(and_(Folder.folder_id is None,
                                              Folder.project_id is None,
                                              Folder.name == folder_name,
                                              Folder.status != 'archived'))
        folder = query.all()
        if (len(folder) == 1):
            folder = folder[0]
        elif (len(folder) == 0):
            # TODO: Create attachment folder
            folder = self._ctx.run_command('folder::new', values={ 'name':       folder_name,
                                                                   'project_id': None },
                                                          folder = folder )
        else:
            raise CoilsException('Found multiple attachment folders for objectId#{0}'.format(self._object.object_id))
        extension    = self._name.split('.')[-1]
        base_name    = '.'.join(self._name.split('.')[:-1])
        ls = self._ctx.run_command('folder::ls', id = folder.object_id)
        for entry in ls:
            if (entry.__entityName__ == 'Document'):
                if entry.name == base_name and entry.extension == extension:
                    # TODO: Update
                    self._ctx.run_command('document::update', object=entry, values = { })
                    break
        else:
            # TODO: Create new document

        self._result = self.obj
