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
import io, yaml
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from workflow                          import WorkflowPresentation
from schedule            import Schedule

class ScheduleObject(DAVObject, WorkflowPresentation, Schedule):
    ''' Represents a workflow message in a process with a DAV hierarchy. '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self.schedule = None

    def get_property_webdav_getetag(self):
        return self.name

    def get_property_webdav_displayname(self):
        return self.name

    def get_property_webdav_getcontentlength(self):
        #if (self._get_representation()):
        #    return str(len(self.data))
        return str('0')

    def get_property_webdav_getcontenttype(self):
        return 'text/yaml'

    def get_property_webdav_creationdate(self):
        return datetime.now()

    def update(self, payload):
        return yaml.dump(self.diff_schedule(payload))

    def do_HEAD(self):
        self.get_schedule()
        representation = self.render_schedule()
        self.log.debug(representation)
        self.request.simple_response(201,
                             mimetype = 'text/plain',
                             headers  = { 'Content-Length':                 len(self.representation),
                                          'ETag':                           self.get_property_webdav_getetag() } )

    def do_GET(self):
        self.get_schedule()
        representation = self.render_schedule()
        if (representation is None):
            raise CoilsException('Unable to marshal workflow schedule for this mode.')
        self.log.debug(representation)
        self.request.simple_response(200,
                                     data=representation,
                                     mimetype='text/plain',
                                     headers={
                                         'ETag':                           self.get_property_webdav_getetag()
                                     } )
