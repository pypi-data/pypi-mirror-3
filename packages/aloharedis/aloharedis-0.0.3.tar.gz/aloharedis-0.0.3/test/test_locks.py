# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import time
from threading import Thread
import redis
import aloharedis
assert aloharedis.__version__ == '0.0.3'
from aloharedis.locks import *

from nose.tools import *

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! IMPORTANT: We use redis db=7 for these tests   !!!
# !!! and will DELETE ALL DATA from it after tested. !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DB = 7

def setup_module():
    global redis_client
    redis_client = redis.StrictRedis(db=DB)
    redis_client.flushdb()


def teardown_module():
    redis_client.flushdb()

monitor = list()

def run_block(num, locks):
    lock = locks['lock']
    got = lock.acquire(True)
    start = time.time()
    time.sleep(0.1)
    end = time.time()
    if got:
        monitor.append((num, start, end))
        lock.release()

def run_nonblock(num, locks):
    lock = locks['lock']
    got = lock.acquire(False)
    start = time.time()
    time.sleep(0.5)
    end = time.time()
    if got:
        monitor.append((num, start, end))
        lock.release()

def run_block_with_wait(num, locks):
    lock = locks['lock']
    got = lock.acquire(True, 0.5)
    start = time.time()
    time.sleep(0.1)
    end = time.time()
    if got:
        monitor.append((num, start, end))
        lock.release()

def test1():
    locks = LockManager(redis_client)
    with locks['a']:
        eq_(['<LOCK>a'], locks.keys())
    eq_([], locks.keys())

def test2():
    global monitor
    locks = LockManager(redis_client)
    locks.configure('lock')
    thlist = list()
    num = 10
    thlist = list()
    monitor = list()
    for i in range(num):
        t = Thread(target=run_block, args=(i+1, locks))
        t.start()
        thlist.append(t)
    for t in thlist:
        t.join()
    eq_(num, len(monitor))
    for i in range(num-1):
        p = monitor[i]
        n = monitor[i+1]
        ok_(n[1]>p[2])
    thlist = list()
    monitor = list()
    for i in range(num):
        t = Thread(target=run_nonblock, args=(i+1, locks))
        t.start()
        thlist.append(t)
    for t in thlist:
        t.join()
    eq_(1, len(monitor))
    thlist = list()
    monitor = list()
    for i in range(num):
        t = Thread(target=run_block_with_wait, args=(i+1, locks))
        t.start()
        thlist.append(t)
    for t in thlist:
        t.join()
    ok_(num>len(monitor))
    ok_(1<len(monitor))


