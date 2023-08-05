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
from sqlalchemy import *
from coils.core import *
from services.orm import SearchVector

class VistaSearchCommand(Command):
    __domain__ = "vista"
    __operation__ = "search"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        
        self.keywords = params.get('keywords', [ ])
        if isinstance(self.keywords, basestring):
            self.keywords = self.keywords.split(',')
            
        self.include_archived = params.get('include_archived', False)
        
        self.entity_types     = params.get('entity_types', None)
        
    def run(self, **params):
        filename = None
        db = self._ctx.db_session()
        tsq = func.to_tsquery('english', ' & '.join(self.keywords))
        query = db.query(SearchVector.object_id).filter(SearchVector.vector.op('@@' )(tsq))
        if not self.include_archived:
            query = query.filter(SearchVector.archived == False)
        if self.entity_types:
            # Entity names in search vectors are all lower case; in this case we
            # discard with the Omphalos capitolization of first-class entities
            # rule.  The point of vista-search is to be *FAST*!.
            entity_types = [ x.lower() for x in self.entity_types ]
            query = query.filter(SearchVector.entity.in_(entity_types))
        self.set_result(self._ctx.type_manager.get_entities([ record[0] for record in query.all() ]))
        
