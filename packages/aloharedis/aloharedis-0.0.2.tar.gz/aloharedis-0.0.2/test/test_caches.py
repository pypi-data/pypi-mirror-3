# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import time
import uuid
from datetime import datetime
from random import random
import redis
import aloharedis
assert aloharedis.__version__ == '0.0.2'
from aloharedis.caches import *

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


def test1():
    c = CacheManager(redis_client, default_timeout=1)
    eq_(None, c.get('a'))
    data = uuid.uuid4()
    c.set('a', data)
    eq_(data, c.get('a'))
    c.delete('a')
    eq_(None, c.get('a'))
    c.set('a', data)
    time.sleep(2)
    eq_(None, c.get('a'))
    c.set('a', 1)
    c.set('b', 2)
    c.set('c', 3)
    eq_([1,2,3,None], c.get_many('a', 'b', 'c', 'd'))
    eq_(dict(a=1,b=2,c=3,d=None), c.get_dict('a', 'b', 'c', 'd'))
    c.add('a', 100)
    eq_(1, c.get('a'))
    c.set_many(dict(x=1,y=2,z=3))
    eq_([1,2,3], c.get_many('x', 'y', 'z'))
    eq_(2, c.inc('x'))
    eq_(4, c.inc('x', 2))
    eq_(2, c.dec('x', 2))
    eq_(1, c.dec('x'))
    c.delete_many('x','y','z')
    eq_([None,None,None], c.get_many('x', 'y', 'z'))
    c.set('a', 'x', 10)
    time.sleep(2)
    eq_(['x', None], c.get_many('a', 'b'))
    eq_(['<CACHE>a'], c.keys())
    c.clear()
    eq_([], c.keys())


def test_ts_as_timeout():
    c = CacheManager(redis_client)
    n = int(time.time())
    c.set('a', 'xxx', n+2)
    eq_('xxx', c.get('a'))
    time.sleep(3)
    eq_(None, c.get('a'))
    