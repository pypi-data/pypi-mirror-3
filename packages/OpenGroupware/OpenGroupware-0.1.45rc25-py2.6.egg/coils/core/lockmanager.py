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

    def _lock_to_lockinfo(self, lock):
        return { 'token':     lock.token,
                 'objectId':  lock.object_id,
                 'ownerId':   lock.owner_id,
                 'expires':   lock.expires,
                 'granted':   lock.granted,
                 'kind':      lock.kind,
                 'owner':     json.loads(lock.data),
                 'exclusive': lock.exclusive }

    def locks_on(self, entity, write=True, exclusive=True):
        db = self._ctx.db_session()
        t = self._now()
        query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                           Lock.granted < t,
                                           Lock.expires > t ) )
        data = query.all()
        query = None
        return data

    def lock(self, entity, duration, data, exclusive=True):
        db = self._ctx.db_session()
        locks = self.locks_on(entity, exclusive=exclusive)
        if (len(locks) == 0):
            lock = Lock(self._ctx.account_id, entity.object_id, duration, data)
            self._ctx.db_session().add(lock)
            return self._lock_to_lockinfo(lock)
        else:
            for lock in locks:
                if (lock.owner_id == self._ctx.account_id):
                    t = self._now()
                    lock.granted = t
                    lock.expires = t + duration
                    return self._lock_to_lockinfo(lock)
            else:
                # Someone else has object locked
                return None

    def refresh(self, token, duration):
        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter(and_(Lock.token == token,
                                           Lock.owner_id  == self._ctx.account_id,
                                           Lock.granted < t,
                                           Lock.expires > t ) )
        data = query.first()
        if (data is not None):
            data.granted = self._now()
            data.expires = self._now() + duration
            return self._lock_to_lockinfo(data)
        return None


    def unlock(self, entity, token=None):
        db = self._ctx.db_session()
        if (token is None):
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == self._ctx.account_id))
        else:
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == self._ctx.account_id,
                                               Lock.token     == token ) )
        for lock in query.all():
            self._ctx.db_session().delete(lock)

    def get_lockinfo(self, token):
        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter(and_(Lock.token == token,
                                           Lock.owner_id  == self._ctx.account_id,
                                           Lock.granted < t,
                                           Lock.expires > t ) )
        data = query.first()
        if (data is not None):
            return self._lock_to_lockinfo(data)
        return None

    def is_locked(self, entity, write=True, exclusive=True):
        locks = self.locks_on(entity)
        if (len(locks) > 0):
            return True
        return False

    def have_lock(self, entity, write=True, exclusive=True):
        locks = self.locks_on(entity)
        for lock in locks:
            if lock.owner_id == self._ctx.account_id:
                return True
        return False
