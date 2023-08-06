# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""
Object Hash Mapper
==================


"""

__all__ = [
    'STATE_NEW', 'STATE_DIRTY', 'STATE_UNCHANGED', 'MAX_EXPIRE_SECONDS',
    'Attr', 'EnumAttr', 'NumberAttr', 'IntAttr', 'FloatAttr',
    'TimestampAttr', 'SerialAttr', 'BooleanAttr', 'StringAttr',
    'PeriodSerialAttr', 'UnicodeAttr',
    'Hash', 'Manager'
]

import time
try:
    import cPickle as pickle
except ImportError:
    import pickle
from decimal import Decimal
from redis import WatchError
from .stores import Store
from .serials import SerialsManager, Serial, PeriodSerial, PERIOD_DAILY

STATE_NEW, STATE_DIRTY, STATE_UNCHANGED = 'new', 'dirty', 'unchanged'

MAX_EXPIRE_SECONDS = 946656000  # timestamp of Jan. 1st, 2000
                                # objects' __expired__ large than this
                                # will be treated as a timestamp,
                                # otherwise it will be treated as seconds


class Attr(object):
    """Attributes for Hash Objects
    
    The base Attr using pickle to load and dump data.
    
    Attributes:
    
        name:  attribute name of object in Python
        field: field name of hash in Redis, by default its same as name
        default: default value
        required: Does this attr required? A required attr must not be None.
                  Note that not all Attr subclasses has this options.
    """
    
    def __init__(self, field=None, default=None, required=False):
        self.field = field   # hash field in Redis
        self.name = None     # attribute name in Python
        self.default = default
        self.required = bool(required)
        self.as_key = False

    def get_value(self, obj):
        storage = obj.__ohm_storage__
        if self.name not in storage:
            self.set_value(obj, self.default)
        return storage[self.name]

    def set_value(self, obj, value):
        storage = obj.__ohm_storage__
        if self.as_key and obj.__fixed_keys__ and obj.__ohm_state__!=STATE_NEW:
            raise RuntimeError('cannot change a key attr while '
                               '"__fixed_keys__" is True')
        original = storage.get(self.name, None)
        if obj.__ohm_state__==STATE_UNCHANGED:
            if value!=original or type(value)!=type(original):
                obj.__ohm_state__ = STATE_DIRTY
        storage[self.name] = value

    def validate(self, value):
        if self.required and value == None:
            raise ValueError('"%s" is required but it is None' % self.name)

    def dumps(self, obj):
        value = self.get_value(obj)
        self.validate(value)
        data = pickle.dumps(value)
        return data

    def loads(self, obj, data):
        value = pickle.loads(data)
        self.set_value(obj, value)


class EnumAttr(Attr):
    def __init__(self, field=None, default=None, required=False,
                 values=None):
        if type(values) not in [tuple, list, set]:
            raise TypeError('"values" should be tuple, list or set')
        values = list(values)
        Attr.__init__(self, field, default, required)
        if not self.required:
            values.append(None)
        if self.default!=None and self.default not in values:
            raise ValueError('"default" neither in values nor None')
        self.values = set(values)

    def validate(self, value):
        if value not in self.values:
            raise ValueError('"%r" is invalid' % value)


class NumberAttr(Attr):
    def __init__(self, field=None, default=Decimal('0'),
                 min_value=None, max_value=None):
        Attr.__init__(self, field, default, True)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value):
        if self.min_value != None and value < self.min_value:
            raise ValueError('value is too small')
        if self.max_value != None and value > self.max_value:
            raise ValueError('value is too large')
    
    def set_value(self, obj, value):
        value = Decimal(value)
        Attr.set_value(self, obj, value)

    def dumps(self, obj):
        value = self.get_value(obj)
        self.validate(value)
        return str(value)

    def loads(self, obj, data):
        self.set_value(obj, data)


class IntAttr(NumberAttr):
    def __init__(self, field=None, default=0, as_key=False,
                 min_value=None, max_value=None):
        self.as_key = bool(as_key)
        NumberAttr.__init__(self, field, default, min_value, max_value)

    def set_value(self, obj, value):
        value = int(value)
        self.validate(value)
        Attr.set_value(self, obj, value)


class TimestampAttr(IntAttr):
    def __init__(self, field=None, default=None):
        IntAttr.__init__(self, field, default, False, 0, 2**32-1)

    def set_value(self, obj, value):
        if value==None:
            value = int(time.time())
        IntAttr.set_value(self, obj, value)    


class SerialAttr(IntAttr):
    def __init__(self, field=None, default=None, as_key=False):
        IntAttr.__init__(self, field, default, as_key, None, None)

    def set_value(self, obj, value):
        if value!=None:
            IntAttr.set_value(self, obj, value)
        else:
            Attr.set_value(self, obj, value)
    
    def dumps(self, obj):
        value = self.get_value(obj)
        if value==None:
            classname = obj.__class__.__name__
            name = '%s.%s' % (classname, self.field)
            serials = obj.manager.serials
            if not serials.has_serial(name):
                serial = Serial(name, pattern=u'%d')
                serials.add_serial(serial)
            value = serials.incr(name)
            self.set_value(obj, value)
        return str(value)


class FloatAttr(NumberAttr):
    def __init__(self, field=None, default=0.0,
                 min_value=None, max_value=None):
        NumberAttr.__init__(self, field, default, min_value, max_value)

    def set_value(self, obj, value):
        # NOTE: Just use str() may cause a problem:
        #
        # >>> 1234567890.1234567890
        # 1234567890.1234567
        # >>> str(1234567890.1234567890)
        # '1234567890.12'
        # >>> float(_)
        # 1234567890.12
        #
        # So we use decimal.Decimal for converting:
        #
        # >>> 1234567890.1234567890
        # 1234567890.1234567
        # >>> decimal.Decimal(1234567890.1234567890)
        # Decimal('1234567890.1234567165374755859375')
        # >>> float(_)
        # 1234567890.1234567
        # >>> str(decimal.Decimal(1234567890.1234567890))
        # '1234567890.1234567165374755859375'
        # >>> float(_)
        # 1234567890.1234567
        value = float(Decimal(value))
        Attr.set_value(self, obj, value)

    def dumps(self, obj):
        value = self.get_value(obj)
        self.validate(value)
        # without help of Decimal, dump a float then load it
        # may result a slightly different value
        data = str(Decimal(value))
        return data


class BooleanAttr(Attr):
    def __init__(self, field=None, default=None, required=False):
        Attr.__init__(self, field, default, required)

    def set_value(self, obj, value):
        value = str(value).strip().lower()
        if value in ['true', 'yes', 'on', 't', 'y', '1']:
            value = True
        elif value in ['false', 'no', 'off', 'f', 'n', '0']:
            value = False
        elif value in ['none', 'null', 'nil', 'n/a', 'na', '~', '']:
            value = None
        else:
            raise TypeError('unsupport value BooleanAttr value type')
        Attr.set_value(self, obj, value)

    def dumps(self, obj):
        value = self.get_value(obj)
        self.validate(value)
        if value:
            data = 'y'
        elif value == False:
            data = 'n'
        else:
            data = '~'
        return data

    def loads(self, obj, data):
        self.set_value(obj, data)


class StringAttr(Attr):
    def __init__(self, field=None, default='', as_key=False,
                 min_length=0, max_length=None, encoding='utf8'):
        Attr.__init__(self, field, default, True)
        self.as_key = bool(as_key)
        self.min_length = min_length
        self.max_length = max_length
        self.encoding = encoding
    
    def validate(self, value):
        if len(value) < self.min_length:
            raise ValueError('value is too short')
        if self.max_length != None and len(value) > self.max_length:
            raise ValueError('value is too long')
    
    def set_value(self, obj, value):
        if type(value) not in [int, long, str, unicode]:
            raise TypeError('unsupport StringAttr value type')
        if type(value)==unicode:
            value = value.encode(self.encoding)
        else:
            value = str(value)
        Attr.set_value(self, obj, value)

    def dumps(self, obj):
        value = self.get_value(obj)
        self.validate(value)
        return value

    def loads(self, obj, data):
        self.set_value(obj, data)


class PeriodSerialAttr(StringAttr):
    def __init__(self, field=None, default=None, as_key=False,
                 min_length=0, max_length=None, encoding='utf8',
                 period=PERIOD_DAILY, pattern=u'%(moment)s%(number)08d',
                 moment_format=None):
        StringAttr.__init__(self, field, default, as_key, None, None, encoding)
        self.period = str(period)
        self.pattern = unicode(pattern)
        self.moment_format = unicode(moment_format) if moment_format else None

    def set_value(self, obj, value):
        if value!=None:
            StringAttr.set_value(self, obj, value)
        else:
            Attr.set_value(self, obj, value)
    
    def dumps(self, obj):
        value = self.get_value(obj)
        if value==None:
            classname = obj.__class__.__name__
            name = '%s.%s' % (classname, self.field)
            serials = obj.manager.serials
            if not serials.has_serial(name):
                serial = PeriodSerial(name, self.period, pattern=self.pattern,
                                      moment_format=self.moment_format)
                serials.add_serial(serial)
            value = serials.incr(name)
            self.set_value(obj, value)
        return str(value)


class UnicodeAttr(StringAttr):

    def set_value(self, obj, value):
        if type(value) not in [int, long, str, unicode]:
            raise TypeError('unsupport UnicodeAttr value type')
        if type(value)==str:
            value = value.decode(self.encoding)
        else:
            value = unicode(value)
        Attr.set_value(self, obj, value)
    
    def dumps(self, obj):
        value = self.get_value(obj)
        self.validate(value)
        return value.encode(self.encoding)


class HashMeta(type):
    def __new__(class_, name, bases, dict_):
        meta = dict(
            attrs=dict(),   # attr name => instance of Attr
            names=dict(),   # redis field name => ohm attr name
            keys=list(),    # list of attr names which has been marked as_key
        )
        for base_class in bases:
            if hasattr(base_class, '__ohm_meta__'):
                super_meta = base_class.__ohm_meta__
                meta['attrs'].update(super_meta['attrs'])
                meta['names'].update(super_meta['names'])
                meta['keys'].extend(super_meta['keys'])
        for itemname in dict_:
            attr = dict_[itemname]
            if isinstance(attr, Attr):
                attr.name = itemname
                if not attr.field:
                    attr.field = itemname
                meta['attrs'][attr.name] = attr
                meta['names'][attr.field] = attr.name
                if attr.as_key:
                    meta['keys'].append(attr.field)
        for itemname in meta['attrs']:
            attr = meta['attrs'][itemname]
            dict_[itemname] = property(attr.get_value, attr.set_value)
        dict_['__ohm_meta__'] = meta
        return type.__new__(class_, name, bases, dict_)


class Hash(object):
    """Hash
    """
    __metaclass__ = HashMeta
    __expired__ = 0
    __fixed_keys__ = False
    __ensure_new__ = False
    
    def __new__(class_, *args, **kwargs):
        obj = super(Hash, class_).__new__(class_)
        obj.__ohm_storage__ = dict()
        obj.__ohm_manager__ = None
        obj.__ohm_state__ = STATE_NEW
        meta = class_.__ohm_meta__
        if not meta['keys']:
            field = '_id'
            attr = SerialAttr(field, as_key=True)
            attr.name = field
            meta['attrs'][attr.name] = attr
            meta['names'][attr.field] = attr.name
            meta['keys'].append(attr.field)
            setattr(class_, attr.name, property(attr.get_value, attr.set_value))
        meta['keys'].sort()
        return obj

    @classmethod
    def _get_attrs(cls):
        meta = cls.__ohm_meta__
        return meta['attrs'].copy()
    
    @classmethod
    def _get_attr_by_name(cls, name):
        return cls._get_attrs()[name]
    
    @classmethod
    def _get_attr_by_filed(cls, field):
        meta = cls.__ohm_meta__
        return cls._get_attr_by_name(meta['names'][field])
    
    @classmethod
    def _get_key_prefix(cls):
        return getattr(cls, '__key_prefix__', cls.__name__)
    
    @classmethod
    def _get_key_sep(cls):
        return getattr(cls, '__key_sep__', ':')
    
    @classmethod
    def _get_key_fields(cls):
        meta = cls.__ohm_meta__
        return meta['keys'][:]

    @classmethod
    def _get_key_pattern(cls):
        meta = cls.__ohm_meta__
        prefix = cls._get_key_prefix()
        sep = cls._get_key_sep()
        fields = cls._get_key_fields()
        if len(fields)==1:
            field = fields[0]
            pattern = '%s%s%%(%s)s' % (prefix, sep, field)
        else:
            pattern = prefix
            for field in fields:
                pattern += '%s%s%s%%(%s)s' % (sep, field, sep, field)
        return pattern

    def _get_key(self, data):
        pattern = self._get_key_pattern()
        return pattern % data
    
    def attach(self, manager):
        if not self.__ohm_manager__:
            self.__ohm_manager__ = manager
        elif self.__ohm_manager__ != manager:
            raise RuntimeError('this object has attached to a manager')
    
    def detach(self):
        self.__ohm_manager__ = None
    
    @property
    def manager(self):
        return self.__ohm_manager__
    
    def save(self, manager=None):
        manager = manager or self.manager
        if not manager:
            raise RuntimeError('this object has not been attached to a manager')
        manager.save(self)

    def _dump(self, manager):
        self.attach(manager)
        data = dict()
        attrs = self._get_attrs()
        for name in attrs:
            attr = attrs[name]
            field = attr.field
            value = attr.dumps(self)
            data[field] = value
        return data
    
    def _load(self, data, manager):
        self.attach(manager)
        for field in data:
            value = data[field]
            try:
                attr = self._get_attr_by_filed(field)
            except KeyError:
                attr = None
            if attr:
                attr.loads(self, value)
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        attrs = self._get_attrs()
        for name in attrs:
            if getattr(self, name) != getattr(other, name, None):
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)


class Manager(Store):
    """Object Hash Mapper Manager
    """

    def __init__(self, store, serials_key='<OHM-SERIALS>'):
        Store.__init__(self, store)
        self.serials = SerialsManager(store, str(serials_key))

    def save(self, obj):
        if not isinstance(obj, Hash):
            raise TypeError('obj should be an instance of Hash')
        # get data and key
        state = obj.__ohm_state__
        expired = int(obj.__expired__)
        data = obj._dump(self)
        key = obj._get_key(data)
        # does "expire" or "expireat" command required?
        expire_required = False
        if state==STATE_NEW and expired!=0:
            expire_required = True
        # save it and expire it if needed
        if state==STATE_NEW and bool(obj.__ensure_new__):
            # if __ensure_new__ is True, work in a transaction
            with self.store.pipeline() as trans:
                try:
                    trans.watch(key)  # watch a nonexistent key is OK
                    if trans.exists(key):
                        raise RuntimeError
                    trans.multi()
                    success = trans.hmset(key, data)
                    # may raise redis.WatchError below
                    trans.execute()
                except (RuntimeError, WatchError):
                    raise RuntimeError('key "%s" exists' % key)
        else:
            # may raise redis.ResponseError below
            success = self.store.hmset(key, data)
        if success:
            obj.__ohm_state__ = STATE_UNCHANGED
            if expire_required:
                if expired > MAX_EXPIRE_SECONDS:
                    self.store.expireat(key, expired)
                else:
                    self.store.expire(key, expired)
        return success

    def load(self, class_, key):
        if not issubclass(class_, Hash):
            raise ValueError('argument "class_" should be subclass of Hash')
        data = self.store.hgetall(key)
        if not data:
            return None
        obj = class_()
        obj._load(data, self)
        obj.__ohm_state__ = STATE_UNCHANGED
        return obj
    
    def find(self, class_, *pattern, **kwargs):
        if not issubclass(class_, Hash):
            raise ValueError('argument "class_" should be subclass of Hash')
        if pattern:
            # has pattern, search for "Object:<pattern>"
            # mapping is ignore
            pattern = pattern[0]
            prefix = class_._get_key_prefix()
            sep = class_._get_key_sep()
            pattern = '%s%s%s' % (prefix, sep, pattern)
        elif not kwargs:
            # neither pattern not mapping, search for "Object:*"
            prefix = class_._get_key_prefix()
            sep = class_._get_key_sep()
            pattern = '%s%s*' % (prefix, sep)
        else:
            # only the mapping is given, search for
            # "Object:key1:value1:key2:value2:not-given-key:*"
            key_pattern = class_._get_key_pattern()
            key_fields = class_._get_key_fields()
            for field in key_fields:
                if field not in kwargs:
                    kwargs[field] = '*'
            pattern = key_pattern % kwargs
        keys = self.store.keys(pattern)
        return keys
