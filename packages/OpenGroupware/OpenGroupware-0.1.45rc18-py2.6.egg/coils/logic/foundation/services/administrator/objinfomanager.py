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
from coils.core          import ObjectInfo, Packet

class ObjectInfoManager(object):

    def __init__(self, ctx, log=None, service=None):
        self._ctx = ctx
        self._log = log
        self._srv = service

    def repair(self, object_id):
        kind = self._ctx.type_manager.get_type(object_id)
        if (kind == 'Unknown'):
            self._log.debug('Type of objectId#{0} not found.'.format(object_id))
            return False
        else:
            db = self._ctx.db_session()
            x = db.query(ObjectInfo).filter(ObjectInfo.object_id == object_id).all()
            if (len(x)):
                self._ctx.rollback()
                self._log.debug('Taking no action as objectId#{0} is already known to ObjectInfo'.format(object_id))
                return False
            else:
                # Convert to the Legacy entity name
                if (kind == "Appointment"):   kind = 'Date'
                elif (kind == "Task"):        kind = 'Job'
                elif (kind == "Contact"):     kind = 'Person'
                elif (kind == "Resource"):    kind = 'AppointmentResource'
                elif (kind == "participant"): kind = 'DateCompanyAssignment'
                elif (kind == "Document"):    kind = 'Doc'
                x = ObjectInfo(object_id, kind)
                self._log.debug('Recording objectId#{0} as a "{1}" into ObjectInfo'.format(object_id, kind))
                self._ctx.db_session().add(x)
                self._ctx.commit()
                return True