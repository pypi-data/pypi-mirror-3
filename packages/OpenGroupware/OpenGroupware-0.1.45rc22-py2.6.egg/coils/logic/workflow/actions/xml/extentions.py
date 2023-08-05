#
# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime import datetime
from coils.logic.workflow.tables import Table

# TODO: Maybe we can generalize this somewhere so it can be found
#       and used for XSLT and XPath commonly?  
class OIEXSLTExtensionPoints:
    
    def __init__(self, process, context, scope, ctxids):
        self.process = process
        self.context = context
        self.scope   = scope
        self.ctxids  = ctxids
        self.tables  = { }

    def shutdown(self):
        for name, table in self.tables.items():
            table.shutdown()

    def _get_sequence_value(self, scope, name):
        
        sequence_target = None
        if scope == 'process':
            sequence_target = self.process
        elif scope == 'route':
            sequence_target = self.process.route
        elif scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException('Invalid execution path! Possible security model violation.')
        
        if not sequence_target:
            raise CoilsException('Unable to determine the target for scope of sequence "{0}"'.format(name))
            
        name = 'sequence_{0}'.format(name)                
            
        prop = self.context.property_manager.get_property(sequence_target, 'http://www.opengroupware.us/oie', name)
            
        if prop:
            value = prop.get_value()
            try:
                value = long(value)
            except:
                error = 'Workflow sequence value is corrupted: sequence={0} value="{1}" scope={2}'.format(name, value, scope)
                raise CoilsException(error)
            return value
        else:
            raise CoilsException('No such sequence as "{0}" in scope "{1}" for processId#{2}.'.format(name, scope, self.process.object_id))            
            
    def _set_sequence_value(self, scope, name):
        
        sequence_target = None
        if scope == 'process':
            sequence_target = self.process
        elif scope == 'route':
            sequence_target = self.process.route
        elif scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException('Invalid execution path! Possible security model violation.')
        
        if not sequence_target:
            raise CoilsException('Unable to determine the target for scope of sequence "{0}"'.format(name))        
            
        name = 'sequence_{0}'.format(name)
            
        self.context.property_manager.set_property(sequence_target, 'http://www.opengroupware.us/oie', name, long(value))            

    def sequencevalue(self, _, scope, name):
        # TODO: Test
        return self._get_sequence_value(scope, name)

    def sequencereset(self, _, scope, name, value):
        # TODO: Test
        self._set_sequence_value(scope, name, value)

    def sequenceincrement(self, _, scope, name, increment):
        # TODO: Test
        value = self._get_sequence_value(scope, name)
        value += increment
        self._set_sequence_value(scope, name, value)
        return unicode(value)
        
    def messagetext(self, _, label):
        data = self.context.run_command('message::get-text', process=self.process,
                                                             scope=self.scope,
                                                             label=label)
        if not data:
            return ''
        return data
                
    def searchforobjectid(self, _, domain, *args):
        args = list(args)
        criteria = [ ]
        while len(args) > 0:
            criteria.append( { 'key': args.pop(0), 'value': args.pop(0) } )
        result = self.context.run_command('{0}::search'.format(domain), criteria=criteria, 
                                                                        contexts=self.ctxids )
        if len(result) == 1:
            result = result[0]
            if hasattr(result, 'object_id'):
                return unicode(result.object_id)
        return ''            

    def tablelookup(self, _, name, value):
        if name not in self.tables:
            self.tables[name] = Table.Load(name)
        table = self.tables[name]
        return unicode(table.lookup_value(value))
        
    def reformatdate(self, _, value, format):
        value = value.strip()
        if len(value) == 10:
            value = datetime.strptime(value.strip(), '%Y-%m-%d')
        elif len(value) == 19:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            raise CoilsException('Call to reformatdate with value not a StandardXML formatted date: "{0}"'.format(value))
        return value.strftime(format)
