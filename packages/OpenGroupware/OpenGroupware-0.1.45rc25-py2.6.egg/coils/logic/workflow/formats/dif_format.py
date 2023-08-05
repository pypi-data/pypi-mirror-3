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
import StringIO
import api_dif  as dif
from lxml        import etree
from format      import COILS_FORMAT_DESCRIPTION_OK, Format

# WARN: Current import only
class SimpleDIFFormat(Format):
    #TODO: Import export support (low-priority)

    def __init__(self):
        Format.__init__(self)
        self._styles = None

    def set_description(self, fd):
        code = Format.set_description(self, fd)
        if (code[0] == 0):
            self.description = fd
            self._definition    = self.description.get('data')
            # TODO: Check that every field has at least: kind
            self._skip_lines     = int(self._definition.get('skipLeadingLines', 0))
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    @property
    def mimetype(self):
        # TODO: correct?
        return 'application/dif'

    def process_in(self, rfile, wfile):
        dir(dif)
        self.in_counter = 0
        sheet = dif.DIF(rfile)
        self._input = rfile
        self._result = []
        wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        wfile.write(u'<ResultSet formatName=\"{0}\" className=\"{1}\">'.format(self.description.get('name'),
                                                                              self.__class__.__name__))
        for record in sheet.data:
            data = self.process_record_in(record)
            if (data is not None):
                wfile.write(data)
        wfile.write(u'</ResultSet>')
        return

    def process_record_in(self, record):
        row = []
        self.in_counter = self.in_counter + 1
        if (self.in_counter <= self._skip_lines):
            self.log.debug('skipped initial line {0}'.format(self.in_counter))
            return None
        for field in self._definition.get('columns'):
            # Get value from record; either from a column or specified static value
            if ('column' in field):
                value = str(record[ord(field['column'].upper()) - 65])
            elif ('static' in field):
                value = field['static']
            else:
                raise CoilsException('No column id or static value specified for field.')
            # process value
            if (field.get('strip', False)): value = value.strip()
            if (value == field.get('nullValue', None)):
                isNull = True
            else:
                isNull = False
                if ((field['kind'] == 'integer') or (field['kind'] == 'float')):
                    divisor = field.get('divisor', 1)
                    if (field['sign'] == 'a'):
                        sign  = value[-1:] # Take last character as sign
                        value = value[:-1] # Drop last character
                    elif (field['sign'] == 'b'):
                        sign = value[0:1] # Take first character as sign
                        value = value[1:] # Drop first character
                    else:
                        sign = '+'
                    if (sign == '+'):
                        sign = 1
                    else:
                        sign = -1
                    if (field['kind'] == 'integer'):
                        value = (int(float(value)) * int(sign))
                        if (divisor != 1):
                            value = value / int(divisor)
                    else:
                        value = (float(value) * float(sign))
                        if (divisor != 1):
                            value = value / float(field['divisor'])
                else:
                    value = self.encode_text(value)
            # name, kind, isKey, value
            isKey = str(field.get('key', 'false')).lower()
            if (isNull):
                row.append(u'<{0} dataType=\"{1}\" isNull=\"true\" isPrimaryKey=\"{2}\"/>'.\
                    format(field['name'], field['kind'], isKey))
            else:
                row.append(u'<{0} dataType=\"{1}\" isNull=\"false\" isPrimaryKey=\"{2}\">{3}</{4}>'.\
                    format(field['name'], field['kind'], isKey,  value, field['name']))
        return u'<row>{0}</row>'.format(u''.join(row))

    def process_out(self, rfile, wfile):
        raise NotImplementedException()

    def process_record_out(self, record):
        raise NotImplementedException()
