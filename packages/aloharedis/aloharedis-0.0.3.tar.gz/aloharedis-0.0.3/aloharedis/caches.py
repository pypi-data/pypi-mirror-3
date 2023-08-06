# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license
"""
Caches
======

"""

__all__ = ['CacheManager']

import time
from .stores import PickleStore

MAX_EXPIRE_SECONDS = 946656000  # timestamp of Jan. 1st, 2000
                                # objects' __expired__ large than this
                                # will be treated as a timestamp,
                                # otherwise it will be treated as seconds

class CacheManager(PickleStore):
    """Baseclass for the cache systems.  All the cache systems implement this
    API or a superset of it.

    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`set`.
    """

    def __init__(self, store, key_prefix='<CACHE>', default_timeout=300):
        PickleStore.__init__(self, store)
        if key_prefix:
            self.key_prefix = str(key_prefix)
        else:
            self.key_prefix = ''
        self.default_timeout = default_timeout

    def get(self, key):
        """Looks up key in the cache and returns the value for it.
        If the key does not exist `None` is returned instead.

        :param key: the key to be looked up.
        """
        return PickleStore.get(self, self.key_prefix+key)

    def delete(self, key):
        """Deletes `key` from the cache.  If it does not exist in the cache
        nothing happens.

        :param key: the key to delete.
        """
        self.store.delete(self.key_prefix+key)

    def get_many(self, *keys):
        """Returns a list of values for the given keys.
        For each key a item in the list is created.  Example::

            foo, bar = cache.get_many("foo", "bar")

        If a key can't be looked up `None` is returned for that key
        instead.

        :param keys: The function accepts multiple keys as positional
                     arguments.
        """
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]
        return self.mget(*keys)

    def get_dict(self, *keys):
        """Works like :meth:`get_many` but returns a dict::

            d = cache.get_dict("foo", "bar")
            foo = d["foo"]
            bar = d["bar"]

        :param keys: The function accepts multiple keys as positional
                     arguments.
        """
        values = self.get_many(*keys)
        result = dict()
        for i in range(len(keys)):
            result[keys[i]] = values[i]
        return result

    def set(self, key, value, timeout=None):
        """Adds a new key/value to the cache (overwrites value, if key already
        exists in the cache).

        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key (if not specified,
                        it uses the default timeout).
        """
        timeout = timeout or self.default_timeout
        if timeout>MAX_EXPIRE_SECONDS:
            timeout = max(0, timeout-int(time.time()))
        if self._dialect=='Redis':
            self.setex(self.key_prefix+key, value, timeout)
        else:
            self.setex(self.key_prefix+key, timeout, value)

    def add(self, key, value, timeout=None):
        """Works like :meth:`set` but does not overwrite the values of already
        existing keys.

        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key or the default
                        timeout if not specified.
        """
        timeout = timeout or self.default_timeout
        if timeout>MAX_EXPIRE_SECONDS:
            timeout = max(0, timeout-int(time.time()))
        success = self.setnx(self.key_prefix+key, value)
        if success:
            self.store.expire(self.key_prefix+key, timeout)

    def set_many(self, mapping, timeout=None):
        """Sets multiple keys and values from a mapping.

        :param mapping: a mapping with the keys/values to set.
        :param timeout: the cache timeout for the key (if not specified,
                        it uses the default timeout).
        """
        timeout = timeout or self.default_timeout
        if timeout>MAX_EXPIRE_SECONDS:
            timeout = max(0, timeout-int(time.time()))
        with self.store.pipeline() as pipe:
            for key in mapping:
                if self._dialect=='Redis':
                    pipe.setex(self.key_prefix+key, mapping[key], timeout)
                else:
                    pipe.setex(self.key_prefix+key, timeout, mapping[key])
            pipe.execute()
            
    def delete_many(self, *keys):
        """Deletes multiple keys at once.

        :param keys: The function accepts multiple keys as positional
                     arguments.
        """
        for key in keys:
            self.delete(key)

    def keys(self):
        return self.store.keys(self.key_prefix+'*')

    def clear(self):
        """Clears the cache.  Keep in mind that not all caches support
        completely clearing the cache.
        """
        if not self.key_prefix:
            return
        keys = self.keys()
        if keys:
            self.store.delete(*keys)

    def inc(self, key, delta=1):
        """Increments the value of a key by `delta`.  If the key does
        not yet exist it is initialized with `delta`.

        For supporting caches this is an atomic operation.

        :param key: the key to increment.
        :param delta: the delta to add.
        """
        return self.store.incr(self.key_prefix + key, delta)

    def dec(self, key, delta=1):
        """Decrements the value of a key by `delta`.  If the key does
        not yet exist it is initialized with `-delta`.

        For supporting caches this is an atomic operation.

        :param key: the key to increment.
        :param delta: the delta to subtract.
        """
        return self.store.decr(self.key_prefix + key, delta)
