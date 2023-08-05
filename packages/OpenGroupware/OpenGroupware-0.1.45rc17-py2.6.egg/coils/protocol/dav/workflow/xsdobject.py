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
import io
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from coils.net.ossf     import MarshallOSSFChain
from workflow           import WorkflowPresentation

class XSDObject(DAVObject, WorkflowPresentation):
    ''' Represents a workflow message in a process with a DAV hierarchy. '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_getetag(self):
        return '{0}:{1}'.format(self.entity.object_id, self.entity.version)

    def get_property_webdav_displayname(self):
        if (hasattr(self.parent, 'label_type')):
            if (self.parent.label_type == 'label'):
                if (self.entity.label is not None):
                    return self.entity.label
        return self.entity.uuid[1:-1]

    def get_property_webdav_getcontentlength(self):
        #if (self._get_representation()):
        #    return str(len(self.data))
        return str(self.entity.size)

    def get_property_webdav_getcontenttype(self):
        return u'text/xml'

    def get_property_webdav_creationdate(self):
        return self.entity.created

    def do_HEAD(self):
        self.request.simple_response(201,
                             mimetype = self.entity.mimetype,
                             headers  = { 'Content-Length':                 str(self.entity.size),
                                          'ETag':                           self.get_property_webdav_getetag() } )

    def do_GET(self):
        handle = self.context.run_command('note::get-handle', id=self.entity.object_id)
        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype=self.entity.get_mimetype(),
                                     headers={ 'etag': self.get_property_webdav_getetag() } )
