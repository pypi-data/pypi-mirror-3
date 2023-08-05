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
# THE SOFTWARE.
#
import hashlib
from coils.net                         import DAVFolder
import projectfolder

class ProjectsSubFolder(DAVFolder):
    ''' Provides a WebDAV collection containing all the projects (as
        subfolders) which the current account has access to,'''

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        children = self.context.run_command('project::get-projects', project=self.entity)
        for project in children:
            self.insert_child(project.number, project, alias=project.object_id)
        return True

    def _get_project_for_key(self, key):
        try:
            object_id = int(str(key).split('.')[0])
        except:
            # TODO: Raise an exception
            pass
        project = self.context.run_command('project::get', id = object_id)

    def _get_project_for_name(self, name):
        project = self.context.run_command('project::get', number=name)
        if (project is not None):
            return project
        project = self.context.run_command('project::get', name=name)
        if (project is not None):
            return project
        try:
            object_id = int(name)
        except:
            return None
        return self.context.run_command('project::get', id=object_id)

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self._get_ctag()

    def _get_ctag(self):
        if (self.load_contents()):
            m = hashlib.md5()
            for entry in self.get_children():
                m.update('{0}:{1}'.format(entry.object_id, entry.version))
            return unicode(m.hexdigest())
        return u'0'

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (self.is_loaded):
            project = self.get_child(name)
        else:
            project = self._get_project_for_name(name)
            if (project is None):
                name = name.replace('(', '%28').replace(')', '%29')
                project = self._get_project_for_name(name)
        if (project is None):
            self.no_such_path()
        else:
            return projectfolder.ProjectFolder(self, project.number,
                                 entity=project,
                                 parameters=self.parameters,
                                 request=self.request,
                                 context=self.context)

