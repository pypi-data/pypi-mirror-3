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
from datetime                  import datetime
from sqlalchemy                import *
import sqlalchemy.orm          as orm
from utcdatetime               import UTCDateTime, UniversalTimeZone
from base                      import Base, KVC
from contact                   import Contact


class Task(Base, KVC):
    """ An OpenGroupare Task object """
    __tablename__       = 'job'
    __entityName__      = 'Task'
    __internalName__    = 'Job'
    object_id           = Column('job_id',
                                ForeignKey('log.object_id'),
                                ForeignKey('job.job_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    version             = Column('object_version', Integer)
    parent_id           = Column('parent_job_id', Integer,
                                 ForeignKey('job.job_id'),
                                 nullable=True)
    project_id          = Column('project_id', Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    creator_id          = Column('creator_id', Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    owner_id            = Column('owner_id', Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    executor_id         = Column('executant_id', Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('team.company_id'),
                                 nullable=True)
    name                = Column('name', String(255))
    start               = Column('start_date', UTCDateTime)
    end                 = Column('end_date', UTCDateTime)
    completed           = Column('completion_date', UTCDateTime, nullable=True)
    notify              = Column('notify_x', Integer)
    state               = Column('job_status', String(255), nullable=False)
    status              = Column('db_status', String(50), nullable=False)
    category            = Column('category', String(255), nullable=True)
    kind                = Column('kind', String(50), nullable=True)
    keywords            = Column('keywords', String(255), nullable=True)
    sensitivity         = Column('sensitivity', Integer)
    priority            = Column('priority', Integer)
    comment             = Column('job_comment', String)
    complete            = Column('percent_complete', Integer)
    actual              = Column('actual_work', Integer)
    total               = Column('total_work', Integer)
    _modified            = Column('last_modified', Integer)
    accounting          = Column('accounting_info', String(255))
    travel              = Column('kilometers', String(255))
    companies           = Column('associated_companies', String(255))
    contacts            = Column('associated_contacts', String(255))
    timer               = Column('timer_date', UTCDateTime(), nullable=True)
    caldav_uid          = Column('caldav_uid', String(100))


    @property
    def modified(self):
        if self._modified:
            return datetime.fromtimestamp(self._modified).replace(tzinfo=UniversalTimeZone())
        return None

    @modified.setter
    def modified(self, value):
        # TODO: Complete
        if value:
            if not value.tzinfo:
                value = value.replace(tzinfo=UniversalTimeZone())
            self._modified = int(value.strftime('%s'))
        else:
            self._modified = None

    def get_display_name(self):
        return self.name

    def get_file_name(self):
        return self.caldav_uid if self.caldav_uid else '{0}.ics'.format(self.object_id)

    @property
    def ics_mimetype(self):
        return 'text/vtodo'

    def __repr__(self):
        return '<Task objectId={0} version={1} name="{2}"' \
                    ' projectId={3} ownerId={4} creatorId={5}' \
                    ' start="{6}" end="{7}" status="{8}">'.\
                format(self.object_id,
                       self.version,
                       self.name,
                       self.project_id,
                       self.owner_id,
                       self.creator_id,
                       self.start.strftime('%Y-%m-%d'),
                       self.end.strftime('%Y-%m-%d'),
                       self.state)

    @property
    def graph_top(self):
        graph = { }
        top = self
        while top.parent:
            top = top.parent
        return top

    @property
    def graph(self):

        def level_down_(task):
            level_ = { }
            for child in task.children:
                level_[child.object_id] = level_down_(child)
            return level_

        top_ = self.graph_top
        return { top_.object_id: level_down_(top_) }


class x1(Base):
    __tablename__ = 'job_history'
    _id            = Column('job_history_id', Integer,
                            Sequence('key_generator'),
                            primary_key=True)
    _task_id       = Column('job_id', Integer,
                            ForeignKey(Task.object_id))
    actor_id      = Column('actor_id', Integer,
                            ForeignKey(Contact.object_id),
                            nullable=False)
    _action        = Column('action', String)
    _action_date   = Column('action_date', UTCDateTime)
    _state         = Column('job_status', String)
    _status        = Column('db_status', String)


class x2(Base):
    __tablename__ = 'job_history_info'
    _info_id      = Column('job_history_info_id', Integer,
                           Sequence('key_generator'),
                           primary_key=True)
    _comment      = Column('comment', String)
    _hist_id      = Column('job_history_id', Integer,
                           ForeignKey(x1._id))
    _status       = Column('db_status', String)


x3 = orm.join(x1, x2)


class TaskAction(Base, KVC):
    """ An OpenGroupare Task History Info entry """
    __table__           = x3
    __entityName__      = 'taskNotation'
    __internalName__    = 'JobHistory'

    status             = orm.column_property(x1._status, x2._status)
    object_id          = orm.column_property(x1._id, x2._hist_id)

    #object_id     = orm.synonym('job_history_id')
    task_id       = orm.synonym('job_id')
    task_status   = orm.synonym('job_status')
    #status        = orm.synonym('db_status')
    date          = orm.synonym('action_date')

    @property
    def owner_id(self):
        return self.task.owner_id
