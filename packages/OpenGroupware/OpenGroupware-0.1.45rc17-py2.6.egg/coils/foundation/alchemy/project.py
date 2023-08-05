#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy     import *
from base           import Base, KVC


class Project(Base, KVC):
    """ An OpenGroupware Project object """
    __tablename__       = 'project'
    __entityName__      = 'Project'
    __internalName__    = 'Project'
    object_id           = Column("project_id",
                                Sequence('key_generator'),
                                ForeignKey('doc.project_id'),
                                ForeignKey('note.project_id'),
                                primary_key=True)
    version             = Column("object_version", Integer)
    owner_id            = Column("owner_id", Integer,
                                ForeignKey('person.company_id'),
                                nullable=False)
    status              = Column("db_status", String(50))
    sky_url             = Column("url", String(100))
    comment             = ''
    end                 = Column("end_date", DateTime())
    kind                = Column("kind", String(50))
    name                = Column("name", String(255))
    number              = Column("number", String(100))
    is_fake             = Column("is_fake", Integer)
    parent_id           = Column("parent_project_id", Integer)
    start               = Column("start_date", DateTime())

    def __init__(self):
        self.status = 'inserted'
        self.version = 0

    def get_display_name(self):
        return self.number

    def __repr__(self):
        return '<Project objectId={0} version={1} name="{2}"' \
                        ' number="{3}" kind="{4}" url="{5}"' \
                        ' fake={6} owner={7} start="{8}"' \
                        ' end="{8}">'.\
                format(self.object_id, self.version, self.name,
                       self.number, self.kind, self.sky_url,
                       self.is_fake, self.owner_id,
                       self.start.strftime('%Y%m%dT%H:%M'),
                       self.end.strftime('%Y%m%dT%H:%M'))

