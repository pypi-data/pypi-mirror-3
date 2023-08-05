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
from coils.foundation import KVC
from coils.core       import Command, CompanyValue
from keymap           import COILS_TELEPHONE_KEYMAP, COILS_ADDRESS_KEYMAP

class CompanyCommand(Command):

    def _list_subtypes_types_for_entity(self, default_name):
        if default_name in ('LSAddressType', 'LSTeleType'):
            # Return address or telephone types
            subtypes = self.sd.default_as_dict(default_name)
            if (self.obj.__internalName__ in subtypes):
                if (isinstance(subtypes[self.obj.__internalName__], list)):
                    return subtypes[self.obj.__internalName__]
                else:
                    raise CoilsException(
                        'Sub-type list {0} in default {1} is improperly structured'.format(
                            self.obj.__internalName__,
                            default_name))
            raise CoilsException(
                'Not sub-type list defined in default {0} for entity type {1}'.format(
                    default_name,
                    str(self.obj)))
        else:
            return []

    def _register_company_value(self, _cv):
        if _cv.name not in self._C_company_values:
            self._C_company_values[_cv.name] = _cv

    def _load_company_values(self):
        query = self._ctx.db_session().query(CompanyValue).filter(CompanyValue.object_id == self.obj.object_id)
        for cv in query.all():
            self._register_company_value(cv)

    def _initialize_company_values(self):
        self._load_company_values()
        subtypes = [ ]
        defaults = [ 'SkyPublicExtended{0}Attributes'.format(self.obj.__internalName__),
                     'SkyPrivateExtended{0}Attributes'.format(self.obj.__internalName__) ]
        for default in defaults:
            for attrdef in self.sd.default_as_list(default, fallback=[]):
                if attrdef['key'] not in self._C_company_values:
                    cv = CompanyValue(self.obj.object_id, attrdef['key'], None)
                    if 'type' in attrdef: cv.widget = attrdef['type']
                    if 'label' in attrdef: cv.label = attrdef['label']
                    self._ctx.db_session().add(cv)
                    self._register_company_value(cv)

    def _set_company_values(self):
        if ('_COMPANYVALUES' not in self.values):
            return

        x = KVC.subvalues_for_key(self.values, ['_COMPANYVALUES'])
        company_values = KVC.keyed_values(x, ['attribute'])
        for attribute in company_values:
            if attribute in self._C_company_values:
                cv = self._C_company_values[attribute]
                # Updating an existing company value ?
                print '-----------'
                import pprint
                pprint.pprint(company_values[attribute])
                print '-----------'
                cv.set_value(company_values[attribute].get('value', None))
                # TODO: or value.widget == 3 ???
                if (attribute[0:5] == 'email'):
                    if ('xattr' in company_values[attribute]):
                        self._ctx.property_manager.set_property(cv, 'http://coils.opengroupware.us/logic', 'xattr01', company_values[attribute].get('xattr'))
                    else:
                        pass
            else:
                # Add new CV
                # TODO: Store label and type
                # TODO: Catch undefine company value attributes
                cv = CompanyValue(self.obj.object_id, attribute, company_values[attribute].get('value', None))
                self._ctx.db_session().add(cv)
                # TODO: or value.widget == 3 ???
                if (cv.name[0:5] == 'email'):
                    if ('xattr' in company_values[attribute]):
                        self._ctx.property_manager.set_property(cv, 'http://coils.opengroupware.us/logic', 'xattr01', company_values[attribute].get('xattr'))
                self._register_company_value(cv)


    def _initialize_telephones(self, kinds):
        # TODO: Read define phone number types from config
        x = KVC.subvalues_for_key(self.values, ['_PHONES', 'telephones', 'phones'])
        telephones = KVC.keyed_values(x, ['kind', 'type'])
        for kind in kinds:
            if (kind in telephones):
                values = telephones[kind]
            else:
                values = { }
            telephone = self._ctx.run_command('telephone::new', values=values,
                                                                parent_id=self.obj.object_id,
                                                                kind=kind)

    def _update_telephones(self, kinds):
        x = KVC.subvalues_for_key(self.values, ['_PHONES', 'telephones', 'phones'])
        telephones = KVC.keyed_values(x, ['kind', 'type'])
        for kind in telephones:
            telephone = KVC.translate_dict(telephones[kind], COILS_TELEPHONE_KEYMAP)
            # Silently filter out telephones of unknown kinds
            if (kind in kinds):
                self._ctx.run_command('telephone::set', values=telephone,
                                                        kind=kind,
                                                        parent_id=self.obj.object_id)

    def _initialize_addresses(self, kinds):
        # TODO: Read defined address types from config
        x = KVC.subvalues_for_key(self.values, ['_ADDRESSES', 'addresses'])
        addresses = KVC.keyed_values(x, ['kind', 'type'])
        for kind in kinds:
            if (kind in addresses):
                values = addresses[kind]
            else:
                values = { }
            address = self._ctx.run_command('address::new', values=values,
                                                            parent_id=self.obj.object_id,
                                                            kind=kind)

    def _update_addresses(self, kinds):
        x = KVC.subvalues_for_key(self.values, ['_ADDRESSES', 'addresses'])
        addresses = KVC.keyed_values(x, ['kind', 'type'])
        for kind in addresses:
            address = addresses.get(kind)
            address = KVC.translate_dict(address, COILS_ADDRESS_KEYMAP)
            # Silently filter out addresses of unknown kinds
            if (kind in kinds):
                self._ctx.run_command('address::set', values=address,
                                                      kind=kind,
                                                      parent_id=self.obj.object_id)
            else:
                raise CoilsException('no such address kind as {0}'.format(kind))

    def _set_comment_text(self):
        comment_text = self.values.get('comment', None)
        if (comment_text is not None):
            self._ctx.run_command('company::set-comment-text', parent_id=self.obj.object_id,
                                                               text=self.values['comment'])

    def _set_projects(self):
        assignments = KVC.subvalues_for_key(self.values,
                                         ['_PROJECTS', 'projects'],
                                         default=None)
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('child_id', None))
                if (_id is not None):
                    _ids.append(_id)
            self._ctx.run_command('company::set-projects', company=self.obj, project_ids=_ids)

    def _set_access(self):
        acls = KVC.subvalues_for_key(self.values, ['_ACCESS', 'acls'], None)
        if (acls is not None):
            self._ctx.run_command('object::set-access', object=self.obj, acls=acls)
