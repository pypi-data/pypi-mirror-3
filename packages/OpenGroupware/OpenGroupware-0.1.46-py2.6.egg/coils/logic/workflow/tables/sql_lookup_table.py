#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import logging, inspect, yaml, uuid
from coils.foundation import *
from coils.core       import *
from table            import Table

class SQLLookupTable(Table):
    # TODO: Implement
    
    def __init__(self):
        Table.__init__(self)
        self.db = None
        
    def __repr__(self):
        return '<SQLLookupTable name="{0}" count="{1}"/>'.format(self.name, len(self.c['values']))
        
    def set_description(self, description):
        self.c = description
        raise NotImplementedException()
            
    def lookup_value(self, value):
        if not self.db:
            self.db = SQLConnectionFactory.Connect(self.c['SQLDataSourceName'])
        if self.db:
            cursor = self.db.cursor()
            cursor.execute(self.c['SQLQueryText'], (value, ))
            record = cursor.fetchone()
            if record:
                result = unicode(record[0])
            else:
                result = None
            cursor.close()
            return result
        else:
            raise CoilsException('SQLLookup table unable to establish connection to SQLDataSource "{0}"'.format(self.c['SQLDataSourceName']))
            
