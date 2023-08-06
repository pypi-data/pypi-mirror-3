# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import time
from datetime import datetime
import uuid
import redis
import aloharedis
assert aloharedis.__version__ == '0.0.3'
from aloharedis.stores import *

from nose.tools import *

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! IMPORTANT: We use redis db=7 for these tests   !!!
# !!! and will DELETE ALL DATA from it after tested. !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DB = 7

def setup_module():
    global redis_client
    redis_client = redis.StrictRedis(db=DB)


def teardown_module():
    redis_client.flushdb()


def test_store():
    store = Store(redis_client)
    eq_(None, store.get('a'))
    ok_(store.set('a', 100))
    eq_('100', store.get('a'))
    ok_(store.delete('a'))
    ok_(not store.exists('a'))


def test_pickle_store():
    store = PickleStore(redis_client)
    data= uuid.uuid4()
    ok_(store.set('a', data))
    eq_(data, store.get('a'))
    eq_(data, store.getset('a', 200))
    eq_(200, store.get('a'))
    ok_(store.mset(dict(x=1, y=2, z=3)))
    eq_([1,2,3], store.mget(['x', 'y', 'z']))
    eq_([1,2,3], store.mget('x', 'y', 'z'))
    ok_(store.msetnx(dict(w=4, u=5, v=6)))
    ok_(not store.msetnx(dict(a=1, i=7, j=8, k=9)))
    ok_(store.setnx('b', 2))
    ok_(not store.setnx('b', 3))
    ok_(store.setex('c', 1, 'x'))
    ok_(store.exists('c'))
    time.sleep(2.0)
    ok_(not store.exists('c'))

    
def test_json_store():
    store = JsonStore(redis_client)
    data = [1,2,3]
    ok_(store.set('a', data))
    eq_(data, store.get('a'))
    with assert_raises(TypeError):
        store.set('a', datetime.now())

    
def test_mongo_extended_json_store():
    store = MongoExtendedJsonStore(redis_client)
    data= uuid.uuid4()
    ok_(store.set('a', data))
    eq_(data, store.get('a'))
    moment = datetime.now()
    store.set('a', moment)
    new = store.get('a').replace(tzinfo=None)
    eq_(moment.replace(microsecond=0), new.replace(microsecond=0))
