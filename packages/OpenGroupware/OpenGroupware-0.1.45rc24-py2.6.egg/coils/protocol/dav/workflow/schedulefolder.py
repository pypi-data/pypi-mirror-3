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
import yaml
from tempfile                          import mkstemp
from coils.core                        import *
from coils.net                         import DAVFolder, OmphalosCollection
from signalobject                      import SignalObject
from workflow                          import WorkflowPresentation
from scheduleobject                    import ScheduleObject

class ScheduleFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return False

    def _load_contents(self):
        self.data = { }
        self.insert_child('crontab.yaml', ScheduleObject(self, 'crontab.yaml', mode='cron',
                                                                               parameters=self.parameters,
                                                                               request=self.request,
                                                                               context=self.context))
        self.insert_child('interval.yaml', ScheduleObject(self, 'interval.yaml', mode='interval',
                                                                                 parameters=self.parameters,
                                                                                 request=self.request,
                                                                                 context=self.context))
        self.insert_child('calendar.yaml', ScheduleObject(self, 'calendar.yaml', mode='calendar',
                                                                                 parameters=self.parameters,
                                                                                 request=self.request,
                                                                                 context=self.context))
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (self.load_contents()):
            if (self.has_child(name, supports_aliases=False)):
                return self.get_child(name, supports_aliases=False)
        raise self.no_such_path()

    def do_PUT(self, request_name):
        """ Allows schedules to be updated by editing the YAML presentations """
        try:
            payload = self.request.get_request_payload()
            data    = yaml.load(payload)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Content parsing failed')
        if (self.load_contents()):
            if (self.has_child(request_name, supports_aliases=False)):
                child = self.get_child(request_name, supports_aliases=False)
                x = child.update(data)
                self.request.simple_response(200, data=x, mimetype='text/plain')
            else:
                 raise self.no_such_path()
        else:
            raise CoilsException('Unable to enumerate folder contents')