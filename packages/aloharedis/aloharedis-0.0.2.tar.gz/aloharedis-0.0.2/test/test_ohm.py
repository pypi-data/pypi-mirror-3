# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import time
from datetime import datetime
from random import random
import redis
import aloharedis
assert aloharedis.__version__ == '0.0.2'
from aloharedis.ohm import *

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


class User(Hash):
    username = StringAttr(as_key=True, min_length=3)
    name = UnicodeAttr()
    enabled = BooleanAttr(required=True)
    age = IntAttr()
    random = FloatAttr()

class Customer(User):
    __fixed_keys__ = True
    __ensure_new__ = True
    customer_id = StringAttr(as_key=True, min_length=8)


class ChatLog(Hash):
    __key_sep__ = '|'
    __key_prefix__ = 'chat'
    ts = TimestampAttr()
    username = StringAttr()
    msg = UnicodeAttr()
    def __init__(self, username='', msg=u''):
        self.username = username
        self.msg = msg

class Order(Hash):
    oid = PeriodSerialAttr(as_key=True, pattern='O-%(moment)s-%(number)04d')
    data = Attr()


def test_simple():
    mgr = Manager(redis_client)
    u1 = User()
    u1.username = 'guest'
    u1.name = 'Guest'
    u1.enabled = 'no'
    u1.random = random()
    ok_(type(u1.name)==unicode)
    ok_(type(u1.enabled)==bool)
    ok_(type(u1.age)==int)
    ok_(mgr.save(u1))
    users = mgr.find(User, 'guest')
    ok_('User:guest' in users)
    users = mgr.find(User)
    ok_('User:guest' in users)
    users = mgr.find(User, username='guest')
    ok_('User:guest' in users)
    u = mgr.load(User, users[0])
    eq_(u, u1)
    # __fixed_keys__ is False
    u.username = 'guest1'


def test_inherited():
    mgr = Manager(redis_client)
    u2 = Customer()
    u2.username = 'customer1'
    u2.name = 'Tom Smith'
    u2.enabled = 'yes'
    u2.customer_id = '1234567'
    with assert_raises(ValueError):
        mgr.save(u2)
    u2.customer_id = '12345678'
    mgr.save(u2)
    customers = mgr.find(Customer)
    ok_('Customer:customer_id:12345678:username:customer1' in customers)
    customers = mgr.find(Customer, customer_id=12345678)
    u = mgr.load(Customer, customers[0])
    eq_(u, u2)
    # __fixed_keys__ is True
    with assert_raises(RuntimeError):
        u.username = 'customer2'
    with assert_raises(RuntimeError):
        u2.customer_id = '87654321'
    # __ensure_new is True
    u3 = Customer()
    u3.username = 'customer1'
    u3.name = 'Jim Smith'
    u3.enabled = 'no'
    u3.customer_id = '12345678'
    with assert_raises(RuntimeError):
        mgr.save(u3)

def test_customize_key_serial_timestamp():
    ts = int(time.time())
    mgr = Manager(redis_client)
    log1 = ChatLog('tom', 'Hello! How are you?')
    log2 = ChatLog('joe', 'Fine, thank you! And you?')
    log3 = ChatLog('tom', 'I''m fine, too. Thank you!')
    ok_(mgr.save(log1))
    ok_(mgr.save(log2))
    ok_(mgr.save(log3))
    eq_(1, log1._id)
    eq_(2, log2._id)
    eq_(3, log3._id)
    eq_(log1, mgr.load(ChatLog, 'chat|1'))
    eq_(log2, mgr.load(ChatLog, 'chat|2'))
    eq_(log3, mgr.load(ChatLog, 'chat|3'))
    ok_(abs(log1.ts-ts)<=1)


def test_period_serial():
    mgr = Manager(redis_client)
    o1 = Order()
    eq_(None, o1.oid)
    o1.attach(mgr)
    o1.save()
    ok_(o1.oid.endswith('0001'))
    o2 = Order()
    mgr.save(o2)
    ok_(o2.oid.endswith('0002'))
