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
import os, base64
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from extentions          import OIEXSLTExtensionPoints

class TransformAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "transform"
    __aliases__   = [ 'transformAction' ]
    
    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._output_mimetype

    def do_action(self):
        
        oie_extentions = OIEXSLTExtensionPoints( context=self._ctx, 
                                                 process=self.process, 
                                                 scope=self.scope_stack,
                                                 ctxids=self._ctx_ids )
        
        extensions = etree.Extension( oie_extentions,
                              ( 
                                'sequencereset',      # Reset/set the value of a named sequence
                                'sequencevalue',      # Retrieve the value of a named sequence
                                'sequenceincrement',  # Increment a named sequence, returning the new value
                                'messagetext',        # Retrieve the content of a message by label
                                'searchforobjectid',  # Search for an objectId by criteria
                                'tablelookup',        # Performa table lookup
                                'reformatdate',       # Reformat a StandardXML date to some other format
                              ),
                              ns='http://www.opengroupware.us/oie' )
        
        source = etree.parse(self.rfile)
        
        #xslt = etree.fromstring(self._xslt)
        
        xslt = etree.XSLT(etree.XML(self._xslt), extensions=extensions)
        
        self.wfile.write(unicode(xslt(source)))
        
        oie_extentions.shutdown()
        

    def parse_action_parameters(self):
        self._b64  = self.action_parameters.get('isBase64', 'NO').upper()
        self._xslt = self.action_parameters.get('xslt', None)
                       
        if (self._xslt is None):
            raise CoilsException('No XSLT provided for transform')
        if (self._b64 == 'YES'):
            self._xslt = base64.decodestring(self._xslt.strip())
        else:
            self._xslt = self.decode_text(self._xslt)
            
        # Allow the transform to reduce the security contexts for extension
        # point operations.  It defaults to the full context of the current
        # context.
        ctx_param = self.action_parameters.get('contextIds', None)
        if ctx_param:
            ctx_param = self.process_label_substitutions(ctx_param)
            self._ctx_ids = [int(x) for x in ctx_param.split(',') if x in self._ctx.context_ids]
        else:
            self._ctx_ids = self._ctx.context_ids
            
        self._output_mimetype = self.action_parameters.get('mimetype', 'application/xml')


    def do_epilogue(self):
        pass
