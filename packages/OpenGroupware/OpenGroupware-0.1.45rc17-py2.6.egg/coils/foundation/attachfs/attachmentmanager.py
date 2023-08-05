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
from coils.foundation import *

def AttachmentManager(BLOBManager):

    def __init__(self, entity):
        self._entity = entity

    def _get_subfolder(self):
        return str((self._entity.object_id + 11111)/100)[1:3]

    def get_path(self, document, version=None):
        # AttahcmentFS is a non-versioning store
        path = 'attachments/{0}/{1}/{2}.{3}'.format(subfolder,
                                                           self._get_subfolder(),
                                                           document.object_id,
                                                           document.extension)
        return path

    def create_path(self, document, version):
        # AttahcmentFS is a non-versioning store
        folder_path = 'attachments/{0}/{1}'.format(self._get_subfolder(),
                                                          self._entity.object_id)
        file_name   = '{1}.{2}'.format(document.object_id, document.extension)
        return (folder_path, file_name)
