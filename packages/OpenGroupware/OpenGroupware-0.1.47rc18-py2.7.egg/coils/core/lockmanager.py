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
import uuid, json
from datetime         import datetime
from coils.foundation import Lock
from sqlalchemy       import *


class LockManager(object):
    __slots__ = ('_ctx')

    def __init__(self, ctx):
        self._ctx = ctx

    def _now(self):
        return int(datetime.utcnow().strftime('%s'))

    def locks_on(self, entity, write=True, exclusive=True):
        db = self._ctx.db_session( )
        t = self._now( )
        query = db.query( Lock ).filter( and_( Lock.object_id == entity.object_id,
                                               Lock.granted <= t,
                                               Lock.expires >= t ) )
        return query.all( )

    def lock(self, entity, duration, data, exclusive=True):
        db = self._ctx.db_session( )
        my_lock = None
        locks = self.locks_on( entity, exclusive=exclusive )
        for lock in locks:
            if ( ( lock.owner_id != self._ctx.account_id ) and
                 ( lock.exclusive ) ):
                # Someone else has an exclusive lock on this object
                return False, lock
            elif ( lock.owner_id == self._ctx.account_id ):
                my_lock = lock
        if my_lock:
            return True, self.refresh( token=lock.token, duration=duration, exclusive=exclusive, data=data )
        else:
            my_lock = Lock( owner_id=self._ctx.account_id, object_id=entity.object_id, duration=duration, data=data )
            self._ctx.db_session( ).add( my_lock )
        return True, my_lock

    def refresh(self, token, duration, data=None, exclusive=True):
        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter(and_(Lock.token == token,
                                           Lock.owner_id  == self._ctx.account_id,
                                           Lock.granted <= t,
                                           Lock.expires >= t ) )
        data = query.all()
        if data:
            my_lock = data[ 0 ]
            my_lock.granted = self._now()
            my_lock.expires = self._now() + duration
            return my_lock
        return None


    def unlock(self, entity, token=None):
        db = self._ctx.db_session()
        if token:
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == self._ctx.account_id,
                                               Lock.token     == token ) )
        else:
            
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == self._ctx.account_id))
        for lock in query.all():
            self._ctx.db_session().delete(lock)

    def get_lock(self, token):
        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter(and_(Lock.token == token,
                                           Lock.granted <= t,
                                           Lock.expires >= t ) )
        data = query.all()
        if data:
            return data[ 0 ]
        return None

    def is_locked(self, entity, write=True, exclusive=True):
        locks = self.locks_on(entity, write=write, exclusive=exclusive)
        if locks:
            return True
        return False

    def have_lock(self, entity, write=True, exclusive=True):
        locks = self.locks_on(entity, write=write, exclusive=exclusive)
        for lock in locks:
            if lock.owner_id == self._ctx.account_id:
                return True
        return False
