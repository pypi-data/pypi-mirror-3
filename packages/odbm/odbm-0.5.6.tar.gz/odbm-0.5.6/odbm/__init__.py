#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Object wrapper for key-value db'''
import os
import sys
import time
import copy
import inspect
import marshal
from datetime import datetime, date, timedelta


md = marshal.dumps
ml = marshal.loads

class cached_classmethod(object):
    '''
    Кеширующий classmethod
    '''
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(owner)
        setattr(owner, self.f.__name__, value)
        return value

class Model(object):
    '''
    >>> class Test(Model):
    ...     day     = DateProperty(primary_key=True)
    ...     foo     = Property(default=[1, 2])
    ...     ustr    = UnicodeProperty(key='u')
    ...     cstr    = CompressedStringProperty()
    ...     cuni    = CompressedUnicodeProperty() 
    ...     created = DateTimeProperty(key='c')
    ...     item    = ChoiceProperty(choices=[1, 2, 3])
    ...     item1   = ChoiceProperty(choices=(('a', 'val1'), ('b', 'val2')))
    ...     hash    = Property(default={})
    ...
    ...     __backend__ = staticmethod(lambda: dict())
    
    >>> Test(
    ...     day     = date(2000, 01, 02),
    ...     foo     = [1, u'a', {'a': 'b'}],
    ...     ustr    = u'bbb',
    ...     cstr    = 'ccc' * 1000,
    ...     cuni    = u'eee' * 1000,
    ...     created = datetime.now(),
    ... ).save()
    >>> Test(day=date(1999, 02, 02)).save()
    
    >>> t = Test.get(date(1999, 02, 02))
    >>> t.foo
    [1, 2]
    >>> t.item = 2
    >>> t.item1 = 'val2'
    >>> t.item1 = 'val0'
    Traceback (most recent call last):
        ...
    KeyError: 'val0'
    
    >>> t.hash['a'] = 'b'
    >>> t.save()
    >>> Test.get(date(1999, 02, 02)).hash
    {'a': 'b'}
    
    
    >>> Test.count()
    2
    >>> Test.count(lambda x: x.ustr == u'bbb')
    1
    
    >>> [t.day.year for t in Test.find(
    ...     filter  = lambda x: t.day.year > 1900 and 3 not in x.foo,
    ...     order   = (lambda x: x.day, -1))]
    [2000, 1999]
    
    >>> Test.find_one().delete()
    >>> Test.count()
    1
    '''
    __backend__ = None
    
    @cached_classmethod
    def db(cls):
        '''Lazy db connection'''
        if not cls.__backend__:
            assert 0, 'set __backend__ in model "%s"' % cls.__name__
        return cls.__backend__()
    
    def __init__(self, _raw_dict=None, **kwargs):
        self._cached_data = {}
        if _raw_dict:
            self._data = _raw_dict
        else:
            self._data = {}
            for prop_name, value in kwargs.iteritems():
                if prop_name in self._properties:
                    setattr(self, prop_name, value)
                else:
                    assert 0, 'unknown property: %s' % prop_name
    
    def save(self):
        pk = self._data.pop('__pk__', None)
        if pk is None:
            assert 0, 'not set primary key "%s" on model "%s"' % (
                self._pk_name, self.__class__.__name__)
        for prop, value in self._cached_data.iteritems():
            if isinstance(value, (dict, list)):
                self._data[prop.key] = prop.encode(value)
        self.db[md(pk)] = md(self._data)
        self._data['__pk__'] = pk
        
    @classmethod
    def get(cls, key):
        key = cls._properties[cls._pk_name].encode(key)
        try:
            kw = cls.db[md(key)]
        except KeyError:
            return None
        kw = ml(kw)
        kw['__pk__'] = key
        return cls(kw)
            
    @classmethod
    def find(cls, filter=None, order=None):
        filter = filter or (lambda x: True)
        def filtered():
            for k, v in cls.db.iteritems():
                kw = ml(v)
                kw['__pk__'] = ml(k)
                obj = cls(kw)
                if not filter(obj):
                    continue
                yield obj
        if order:
            order, asc = order if isinstance(order, tuple) else (order, 1)
            items = [(getattr(obj, cls._pk_name), order(obj))
                for obj in filtered()]
            items.sort(key=lambda x: x[1])
            if asc == -1:
                items.reverse()
            return (cls.get(k) for k, v in items)
        else:
            return filtered()

    @classmethod
    def find_one(cls, filter=None, order=None):
        for v in cls.find(filter, order):
            return v

    @classmethod
    def count(cls, filter=None):
        if not filter:
            return len(cls.db)
        i = 0
        for v in cls.find(filter):
            i += 1
        return i
        
    def delete(self):
        pk = self._data.pop('__pk__')
        if pk is None:
            assert 0, 'not set primary key "%s" on model "%s"' % (
                self._pk_name, self.__class__.__name__)
        del self.db[md(pk)]
        self._data = {}

    @cached_classmethod
    def _pk_name(cls):
        ret = [k for k, v in cls._properties.iteritems() if v.key == '__pk__']
        if not ret:
            assert 0, 'primary key in model "%s" not found' % cls.__name__
        return ret[0]
    
    @cached_classmethod
    def _properties(cls):
        '''
        {prop_name: prop}
        '''
        ret = {}
        all_members = {}
        for c in inspect.getmro(cls):
            for k, v in c.__dict__.iteritems():
                if k not in all_members:
                    all_members[k] = v
        keys = []
        for k, prop in all_members.iteritems():
            if hasattr(prop, '__class__') and issubclass(prop.__class__, BaseProperty):
                if not prop.key:
                    prop.key = k
                if prop.key in keys:
                    keyname = 'primary key' if prop.key == '__pk__' else 'key "%s"' % prop.key
                    assert 0, 'multiply %s in model "%s"' % (keyname, cls.__name__)
                ret[k] = prop
                keys.append(prop.key)
        return ret

    def __unicode__(self):
        keys = self._properties.keys()
        values = {}
        for k in keys:
            v = getattr(self, k)
            if isinstance(v, str):
                v = "'%s'" % v
            if isinstance(v, unicode):
                v = "u'%s'" % v
            try:
                v = unicode(v)
                if len(v) > 50:
                    v = v[:50] + ' ...'
            except UnicodeDecodeError:
                v = '- not printable -'
            if k == self._pk_name:
                k += ' (pk)'
            values[k] = v
        max_len = max([len(k) for k in values.keys()])
        ret = self.__class__.__name__ + '(\n'
        tpl = '    %%-%is = %%s' % max_len
        return ret + '\n'.join([tpl % (k, values[k]) for k in values.keys()]) + '\n)'
            
    def __str__(self):
        return self.__unicode__().encode('utf-8')
    
    def as_dict(self, keys=None):
        keys = keys or self._properties.keys()
        return dict((k, getattr(self, k)) for k in keys)


class BaseProperty(object):
    def __init__(self, key=None, default=None, primary_key=False):
        self.key = '__pk__' if primary_key else key
        self.default = default
        self.primary_key = primary_key
        
    def __get__(self, instance, owner):
        if self in instance._cached_data:
            return instance._cached_data[self]
        if self.key in instance._data:
            ret = self.decode(instance._data[self.key])
        elif isinstance(self.default, (dict, list)):
            ret = copy.copy(self.default)
        else:
            ret = self.default
        instance._cached_data[self] = ret
        return ret

    def __set__(self, instance, value):
        instance._cached_data[self] = value
        instance._data[self.key] = self.encode(value)
        
    def __delete__(self, instance):
        if self in instance._cached_data:
            del instance._cached_data[self]
        if self.key in instance._data:
            del instance._data[self.key]
    
    def encode(self, value):
        '''Приведение к маршализируемому типу'''
        return value
        
    def decode(self, value):
        '''Из маршализируемого типа'''
        return value


class Property(BaseProperty):
    pass


class ChoiceProperty(BaseProperty):
    def __init__(self, choices, *args, **kwargs):
        self.set_choices(choices)
        super(self.__class__, self).__init__(*args, **kwargs)
            
    def set_choices(self, choices):
        self.choices = []
        self._choices_kv = {}
        self._choices_vk = {}
        for item in choices:
            k, v = item if isinstance(item, (tuple, list)) else (item, item)
            self.choices.append((k, v))
            self._choices_kv[k] = v
            self._choices_vk[v] = k

    def encode(self, value):
        return self._choices_vk[value]

    def decode(self, value):
        return self._choices_kv[value]


class UnicodeProperty(BaseProperty):
    def encode(self, value):
        return unicode(value)


class DateTimeProperty(BaseProperty):
    def encode(self, value):
        delta = value - value.replace(hour=0, minute=0, second=0, microsecond=0)
        return value.toordinal(), delta.seconds, delta.microseconds

    def decode(self, value):
        return datetime.fromordinal(value[0]) + timedelta(
            seconds=value[1], microseconds=value[2])


class DateProperty(BaseProperty):
    def encode(self, value):
        return value.toordinal()
    def decode(self, value):
        return date.fromordinal(value)


class CompressedStringProperty(BaseProperty):
    def __init__(self, compressor='zlib', compress_level=9, *args, **kwargs):
        __import__(compressor)
        self.compressor = sys.modules[compressor]
        self.compress_level = compress_level
        super(CompressedStringProperty, self).__init__(*args, **kwargs)
    def encode(self, value):
        return self.compressor.compress(value, self.compress_level)
    def decode(self, value):
        return self.compressor.decompress(value)


class CompressedUnicodeProperty(CompressedStringProperty):
    def __init__(self, internal_encoding='utf-8',
                encoding_errors='ignore', *args, **kwargs):
        self.internal_encoding = internal_encoding
        self.encoding_errors = encoding_errors
        super(CompressedUnicodeProperty, self).__init__(*args, **kwargs)
    def encode(self, value):
        value = value.encode(self.internal_encoding, self.encoding_errors)
        return super(CompressedUnicodeProperty, self).encode(value)
    def decode(self, value):
        value = super(CompressedUnicodeProperty, self).decode(value)
        return value.decode(self.internal_encoding, self.encoding_errors)


class CompressedProperty(CompressedStringProperty):
    def __init__(self, dumper='marshal', *args, **kwargs):
        __import__(dumper)
        self.dumper = sys.modules[dumper]
        super(CompressedProperty, self).__init__(*args, **kwargs)
    def encode(self, value):
        value = self.dumper.dumps(value)
        return super(CompressedProperty, self).encode(value)
    def decode(self, value):
        value = super(CompressedProperty, self).decode(value)
        return self.dumper.loads(value)


class DictDBM(dict):
    '''Dummy dbm for tests'''
    def __init__(self, filename=None):
        self.filename = filename
        if filename:
            try:
                super(self.__class__, self).__init__(
                    **marshal.load(open(filename)))
            except IOError:
                pass
    
    def __setitem__(self, key, value):
        super(self.__class__, self).__setitem__(key, value)
        self.save()
        
    def clear(self):
        super(self.__class__, self).clear()
        self.save()
        
    def save(self):
        if self.filename:
            marshal.dump(dict(self), open(self.filename, 'w'))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
