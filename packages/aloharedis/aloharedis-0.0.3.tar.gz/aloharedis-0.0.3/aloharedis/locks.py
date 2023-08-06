# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license
"""
Locks
=====

"""

__all__ = ['Lock', 'LockManager']

import time
from redis import WatchError
from redis.client import Lock as _Lock
import redis
from .stores import Store


class Lock(_Lock):
    # By using redis.client.Lock directly, the unit tests faild sometimes
    # Our solution is using the Redis' transaction to acquire the lock
    
    WAIT_FOREVER = float(2**31+1) # 1 past max unix time

    def acquire(self, blocking=True, max_wait=None):
        """
        Use Redis to hold a shared, distributed lock named ``name``.
        Returns True once the lock is acquired.

        If ``blocking`` is False, always return immediately. If the lock
        was acquired, return True, otherwise return False.
        """
        started = int(time.time())
        if max_wait:
            deadline = started + float(max_wait)
        else:
            deadline = self.WAIT_FOREVER
        sleep = self.sleep
        timeout = self.timeout
        while True:
            got = False
            with self.redis.pipeline() as trans:
                unixtime = int(time.time())
                if unixtime>deadline:
                    return False
                if timeout:
                    timeout_at = unixtime + timeout
                else:
                    timeout_at = Lock.LOCK_FOREVER
                timeout_at = float(timeout_at)
                try:
                    trans.watch(self.name)
                    exists = trans.exists(self.name)
                    trans.multi()
                    if not exists:
                        if timeout:
                            if self._dialect=='Redis':
                                trans.setex(self.name, timeout_at, timeout)
                            else:
                                trans.setex(self.name, timeout, timeout_at)
                        else:
                            trans.set(self.name, timeout_at)
                        trans.execute()
                        self.acquired_until = timeout_at
                        got = True
                except WatchError:
                    pass
            if got:
                return True
            if not blocking:
                return False
            time.sleep(sleep)
    
    @property
    def _dialect(self):
        if isinstance(self.redis, redis.Redis):
            return 'Redis'
        return ''


class LockManager(Store):
    
    def __init__(self, store, key_prefix='<LOCK>',
                 default_timeout=10, default_sleep=0.1):
        Store.__init__(self, store)
        if key_prefix:
            self.key_prefix = str(key_prefix)
        else:
            self.key_prefix = ''
        self.default_timeout = default_timeout
        self.default_sleep = default_sleep
        self._locks = dict()

    def configure(self, name, timeout=None, sleep=None):
        name = str(name)
        timeout = timeout or self.default_timeout
        sleep = sleep or self.default_sleep
        lock = Lock(self.store, self.key_prefix+name, timeout, sleep)
        self._locks[name] = lock
        return lock
    
    def acquire(self, name, blocking=True):
        name = str(name)
        if name not in self._locks:
            self.configure(name)
        return self[name].acquire(blocking)
    
    def release(self, name):
        name = str(name)
        if name not in self._locks:
            self.configure(name)
        self[name].release()
    
    def __getitem__(self, name):
        name = str(name)
        if name not in self._locks:
            self.configure(name)
        return self._locks[name]
    
    def keys(self):
        return self.store.keys(self.key_prefix+'*')
    
    def force_release(self, name):
        name = str(name)
        self.delete(self.key_prefix+name)
