# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import time
from datetime import datetime
import redis
import aloharedis
assert aloharedis.__version__ == '0.0.2'
from aloharedis.serials import *

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


def test_serial():
    store = SerialsManager(redis_client, '<serials>',
        Serial('sn', 1, 2, u'SN:%010d')
    )
    eq_(u'SN:0000000003', store.incr('sn'))     # 1+2
    eq_(u'SN:0000000005', store.incr('sn'))     # 3+2
    eq_(u'SN:0000000008', store.incr('sn', 3))  # 5+3
    eq_(u'SN:0000000010', store.incr('sn', 0))  # 8+2


def test_period():
    fmt = u'%y/%m/%d'
    store = SerialsManager(redis_client, '<serials>',
        PeriodSerial('bills', PERIOD_DAILY,
                     pattern=u'B/%(moment)s/%(number)07d',
                     moment_format=fmt)
    )
    moment = datetime.now().strftime(fmt)
    eq_(u'B/'+moment+u'/0000001', store.incr('bills'))
    eq_(u'B/'+moment+u'/0000002', store.incr('bills'))


def test_outdated():
    period = '%Y%m%d%H%M%S'
    store = SerialsManager(redis_client, '<secondly-serials>',
        PeriodSerial('secondly', period, pattern=u'%(number)d')
    )
    eq_('1', store.incr('secondly'))
    time.sleep(1.0)
    eq_('1', store.incr('secondly'))
    time.sleep(1.0)
    eq_('1', store.incr('secondly'))
    ok_(len(store.keys)==3)
    time.sleep(1.0)
    store.clean()
    ok_(len(store.keys)==0)
