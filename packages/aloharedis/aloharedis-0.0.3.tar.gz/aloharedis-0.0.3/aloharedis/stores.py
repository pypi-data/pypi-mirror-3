# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""
Store
=====


"""

__all__ = ['Redis', 'Store', 'SerializationStore',
           'PickleStore', 'JsonStore', 'MongoExtendedJsonStore']

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except:
    import json
try:
    from bson import json_util
except:
    json_util = None
from redis import Redis
from redis import StrictRedis


class Store(object):
    
    def __init__(self, store):
        if not isinstance(store, StrictRedis):
            raise TypeError('"store" should an instance of redis.StrictRedis')
        if isinstance(store, Redis):
            self._dialect = 'Redis'
        else:
            self._dialect = 'StrictRedis'
        self._store = store
    
    @property
    def store(self):
        return self._store

    def __getattr__(self, name):
        return getattr(self.store, name)


class SerializationStore(Store):
    
    def serialize(self, value):
        # keep integers unserialized so incr() works
        if type(value) in [int, long]:
            return str(value)
        else:
            return '$' + self._serialize(value)
    
    def unserialize(self, value):
        if value!=None:
            if value.startswith('$'):
                return self._unserialize(value[1:])
            else:
                return int(value)

    def _serialize(self, value):
        raise NotImplementedError
    
    def _unserialize(self, value):
        raise NotImplementedError

    def get(self, key):
        value = self.store.get(key)
        return self.unserialize(value)

    def getset(self, key, value):
        value = self.serialize(value)
        value = self.store.getset(key, value)
        return self.unserialize(value)
    
    def mget(self, keys, *args):
        values = self.store.mget(keys, *args)
        for i in range(len(values)):
            values[i] = self.unserialize(values[i])
        return values

    def mset(self, mapping):
        data = dict()
        for key in mapping:
            data[key] = self.serialize(mapping[key])
        return self.store.mset(data)

    def msetnx(self, mapping):
        data = dict()
        for key in mapping:
            data[key] = self.serialize(mapping[key])
        return self.store.msetnx(data)

    def set(self, key, value):
        value = self.serialize(value)
        return self.store.set(key, value)
    
    def setex(self, key, seconds, value):
        if self._dialect=='Redis':
            seconds, value = value, seconds
        value = self.serialize(value)
        if self._dialect=='Redis':
            return self.store.setex(key, value, seconds)
        else:
            return self.store.setex(key, seconds, value)
    
    def setnx(self, key, value):
        value = self.serialize(value)
        return self.store.setnx(key, value)


class PickleStore(SerializationStore):
    
    def _serialize(self, value):
        return pickle.dumps(value)
    
    def _unserialize(self, value):
        return pickle.loads(value)


class JsonStore(SerializationStore):

    def _serialize(self, value):
        return json.dumps(value)
    
    def _unserialize(self, value):
        return json.loads(value)


class MongoExtendedJsonStore(SerializationStore):
    """
    http://www.mongodb.org/display/DOCS/Mongo+Extended+JSON
    """

    def _serialize(self, value):
        return json.dumps(value, default=json_util.default)
    
    def _unserialize(self, value):
        return json.loads(value, object_hook=json_util.object_hook)
