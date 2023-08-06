# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""
Serial Generators
=================

Example
-------

Below is a simple example to show how this module will work::

    >>> import redis
    >>> from aloharedis.serials import *
    >>> store = SerialsManager(redis.Redis(), '<MySerials>',
    ...     Serial('session.id', pattern=u'SID:%032x'),
    ...     PeriodSerial('sale-order', PERIOD_MONTHLY,
                         pattern=u'SO-%(moment)s-%(mumber)06d',
                         moment_format='%Y-%m')
    ... )
    >>> store.incr('session.id')
    u'SID:00000000000000000000000000000001'
    >>> store.incr('sale-order')
    u'SO-2012-06-000001'

"""

__all__ = ['SerialsManager', 'Serial', 'PeriodSerial',
           'PERIOD_YEARLY', 'PERIOD_MONTHLY', 'PERIOD_WEEKLY_SUNDAY_FIRST',
           'PERIOD_WEEKLY_MONDAY_FIRST', 'PERIOD_DAILY', 'PERIOD_HOURLY']

from datetime import datetime
from .stores import Store

PERIOD_YEARLY = '%Y'
PERIOD_MONTHLY = '%Y%m'
PERIOD_WEEKLY_SUNDAY_FIRST = '%Y%U'
PERIOD_WEEKLY_MONDAY_FIRST = '%Y%W'
PERIOD_DAILY = '%Y%m%d'
PERIOD_HOURLY = '%Y%m%d%H'


class Serial(object):

    def __init__(self, name, initial=0, increment=1, pattern=u'%d'):
        self.name = str(name)
        self.initial = int(initial)
        self.increment = int(increment)
        self.pattern = unicode(pattern)
        self._last_field = None

    def format(self, data):
        return self.pattern % data
    
    def next(self, store, key, increment=0):
        return self.format(self._increase(store, key, increment))
    
    def outdated(self, field):
        field = str(field)
        if field==self.name:
            return False # not outdated
        return None      # unknown

    def _increase(self, store, key, increment=0):
        increment = int(increment or self.increment)
        field = self.name
        if self.initial and self._last_field != field:
            store.hsetnx(key, field, self.initial)
        self._last_field = field
        number = store.hincrby(key, field, increment)
        return number


class PeriodSerial(Serial):

    def __init__(self, name, period, initial=0, increment=1,
                 pattern=u'%(moment)s%(number)06d', moment_format=None):
        Serial.__init__(self, name, initial, increment, pattern)
        self.period = str(period)
        self._last_period = None
        if moment_format!=None:
            self.moment_format = unicode(moment_format)
        else:
            self.moment_format = unicode(self.period)
    
    def _increase(self, store, key, increment=0):
        increment = int(increment or self.increment)
        moment = datetime.now()
        field = '{0}:{1}'.format(self.name, moment.strftime(self.period))
        if self.initial and self._last_field != field:
            store.hsetnx(key, field, self.initial)
        self._last_field = field
        number = store.hincrby(key, field, increment)
        return dict(moment=moment.strftime(self.moment_format), number=number)

    def outdated(self, field):
        field = str(field)
        if not field.startswith(self.name+':'):
            return None  # None means unknown
        moment = datetime.now()
        current = '{0}:{1}'.format(self.name, moment.strftime(self.period))
        if field<current:
            return True  # outdated
        else:
            return False # not outdated


class SerialsManager(Store):
    
    def __init__(self, store, key='<SERIALS>', *serials):
        Store.__init__(self, store)
        self._key = str(key)
        self.store.hsetnx(self.key, '<type>', self.__class__.__name__)
        self._serials = dict()
        for serial in serials:
            self.add_serial(serial)

    @property
    def key(self):
        return self._key
    
    def add_serial(self, serial):
        name = str(serial.name)
        if name in self._serials:
            #raise RuntimeError('serial "%s" already registered' % name)
            return False
        self._serials[name] = serial
        return True
    
    def has_serial(self, serial):
        name = str(getattr(serial, 'name', serial))
        return name in self._serials
    
    def remove_serial(self, serial):
        name = str(getattr(serial, 'name', serial))
        return self._serials.pop(name, None)

    def incr(self, name, increment=0):
        name = str(name)
        serial = self._serials[name]
        result = serial.next(self.store, self.key, increment)
        return result
    
    @property
    def keys(self):
        keys = set(self.store.hkeys(self.key))
        if '<type>' in keys:
            keys.remove('<type>')
        return keys

    def clean(self):
        fields = self.keys
        outdateds = set()
        for field in fields:
            for name in self._serials:
                serial = self._serials[name]
                status = serial.outdated(field)
                if status != None:
                    if status:
                        outdateds.add(field)
                    # either True or False means
                    # the serial knows the field
                    break
        for outdated in outdateds:
            self.store.hdel(self.key, outdated)
