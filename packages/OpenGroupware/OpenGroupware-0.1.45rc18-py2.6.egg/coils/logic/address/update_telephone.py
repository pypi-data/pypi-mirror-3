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
from sqlalchemy       import *
from coils.core       import *
from coils.core.logic import UpdateCommand
from keymap           import COILS_TELEPHONE_KEYMAP

class UpdateTelephone(UpdateCommand):
    __domain__ = "telephone"
    __operation__ = "set"

    def __init__(self):
        UpdateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap = COILS_TELEPHONE_KEYMAP
        self.entity = Telephone
        UpdateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters(self, **params)
        # Extract kind
        if ('kind' in params):
            self.kind = params['kind']
        elif ('kind' in self.values):
            self.kind = self.values['kind']
        elif ('type' in self.values):
            self.kind = self.values['type']
        else:
            raise CoilsException('Attempt to create untyped telephone.')
        # Extract parent_id
        if ('parent_id' in params):
            self.parent_id = params['parent_id']
        elif ('companyObjectId' in self.values):
            self.parent_id = self.values['companyObjectId']
        elif ('company_id' in self.values):
            self.parent_id = self.values['company_id']
        else:
            raise CoilsException('Attempt to create unattached telephone.')

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('telephone::get', id=object_id,
                                                        access_check=access_check)

    def get_by_values(self):
        # TODO: If an address of a valid kind is requested but none is found we
        # should create one on-the-fly
        return self._ctx.run_command('telephone::get', kind=self.kind,
                                                        parent_id=self.parent_id,
                                                        access_check=False)

    def set_telephone_type(self):
        if (self.kind is None):
            setattr(self.obj, 'kind', 'undefined')
        else:
            setattr(self.obj, 'kind', self.kind.lower());

    def set_parent_id(self):
        setattr(self.obj, 'parent_id', self.parent_id)

    def run(self):
        if (self.obj is None):
            self.obj = self.get_by_values()
        UpdateCommand.run(self)
        self.set_telephone_type()
        self.set_parent_id()
