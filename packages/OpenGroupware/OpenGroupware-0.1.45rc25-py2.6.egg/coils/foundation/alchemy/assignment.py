#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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


class ProjectAssignment(Base):
    """ An assignment between company objects """
    __tablename__ = 'project_company_assignment'
    object_id = Column('project_company_assignment_id',
                        Integer,
                        Sequence('key_generator'),
                        primary_key=True)
    parent_id = Column('project_id', Integer,
                        ForeignKey('project.project_id'),
                        ForeignKey('job.project_id'),
                        nullable=False)
    child_id  = Column('company_id', Integer,
                        ForeignKey('person.company_id'),
                        ForeignKey('enterprise.company_id'),
                        nullable=False)
    info      = Column('info', String(255))
    rights    = Column('access_right', String(50))

    def __init__(self, project_id, company_id, permissions=None, info=None):
        self.parent_id = project_id
        self.child_id = company_id
        self.info = info
        self.rights = permissions

    @property
    def action(self):
        if self.rights:
            return 'allowed'
        return None

    @property
    def permissions(self):
        return self.rights
        
    @permissions.setter
    def permissions(self, value):
        self.rights = value

    @property
    def context_id(self):
        if self.rights:
            return self.child_id
        return None

class CompanyAssignment(Base):
    """ An assignment between company objects """
    __tablename__ = 'company_assignment'
    object_id = Column("company_assignment_id",
                        Integer,
                        Sequence('key_generator'),
                        primary_key=True)
    parent_id = Column("company_id", Integer,
                        ForeignKey('enterprise.company_id'),
                        ForeignKey('team.company_id'),
                        nullable=False)
    child_id  = Column("sub_company_id", Integer,
                        ForeignKey('person.company_id'),
                        nullable=False)
    info      = ''
    rights    = ''

    def __init__(self, parent_id, child_id):
        self.parent_id = parent_id
        self.child_id = child_id

    def __repr__(self):
        return '<CompanyAssignment assignmentId={0} parentId={1} childId={2}>'\
                .format(self.object_id, self.parent_id, self.child_id)
