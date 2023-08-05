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
import os, base64
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

#TODO: AssignAction needs love!
class AssignAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "assign"
    __aliases__   = [ 'assignAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._output_mimetype

    def do_action(self):
        if (self._xpath is None):
            self.wfile.write(self._default)
        else:
            value = self._default
            doc = etree.parse(self.rfile)
            result = doc.xpath(self._xpath, namespaces=doc.getroot().nsmap)
            if (isinstance(result, list)):
                if (len(result) > 0):
                    self.log.debug('{0} values found for path {1}'.format(len(result), self._xpath))
                    if (result[0] is not None):
                        # TODO: What if this result isn't text?
                        value = str(result[0])
            self.wfile.write(value)

    def parse_action_parameters(self):
        self._xpath           = self.action_parameters.get('xpath', None)
        self._default         = self.action_parameters.get('default', '')
        self._output_mimetype = self.action_parameters.get('mimetype', 'application/xml')
        if (self._xpath is not None):
            self._xpath = self.decode_text(self._xpath)
            if (len(self._xpath) == 0):
                self._xpath = None
            else:
                self._xpath = self.process_label_substitutions(self._xpath)
        if (len(self._default) > 0):
            self._default = self.process_label_substitutions(self._default)

    def do_epilogue(self):
        pass