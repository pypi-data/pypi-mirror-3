#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#
#
# This file is part of pyTickets.
#
#    pyTickets is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyTickets is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyTickets.  If not, see <http://www.gnu.org/licenses/>.
#


__all__ = [
    'FlagsFactoryException',
    'FlagsFactory',
]


import struct
import operator

try:
    from sets import Set as set
except ImportError:
    pass
    




class FlagsFactoryException(Exception):
    pass

class FlagsException(Exception):
    pass


class FlagsBase(object):

    _ignore_invalid_names_on_init = False

    def __init__(self, flags=None, **kw):
        if not flags is None:
            assert type(flags) is long
            self._flags = flags
        for (name,val) in kw.iteritems():
            if not name in self._flagbit:
                if not self._ignore_invalid_names_on_init:
                    msg = 'unknown flag name: "%s"' %name
                    raise FlagsFactoryException(msg)
            else:
                if val:
                    self._flags |= self._flagbit[name]
                else:
                    self._flags &= ~self._flagbit[name]

    def __getitem__(self, name):
        name = name.lower()
        try:
            idx = operator.indexOf(self._flag_names, name)
        except ValueError:
            msg = "Invalid flag name: '{0}'.".format(name)
            msg += " Valid names are: {0}.".format(', '.join(self._flag_names))
            raise FlagsException(msg)
        bit = 1 << idx
        return bool(self._flags & bit)

    def _set(self, name, value):
        if not name in self._flagbit:
            msg = "Unknown flag name: '{0}'".format(name)
            raise FlagsException(msg)
        if value:
            self._flags |= self._flagbit[name]
        else:
            self._flags &= ~self._flagbit[name]

    def set(self, *args, **kw):
        if len(args):
            assert len(args) == 2
            name, value = args
            self._set(name, value)
        for (name, value) in kw.iteritems():
            self._set(name, value)

    @classmethod
    def _deserialize(cls, flags_serialized):
        flags = long(struct.unpack(cls._type, flags_serialized)[0])
        return cls(flags=flags)

    def _serialize(self):
        return struct.pack(self._type, self._flags)

    def subset(self, *names):
        d = {}
        for name in names:
            d[name] = self[name]
        return d

    def _get_d(self):
        d = {}
        for (i,name) in enumerate(self._flag_names):
            bit = 1 << i
            val = bool(self._flags & bit)
            d[name] = val
        return d
    d = property(_get_d)

    def _get_names(self):
        return tuple(self._flag_names)
    names = property(_get_names)

    def sync(self, otherflags):
        '''
            update self with values from otherflags for all matching flag names
        '''
        names = set(self.names) & set(otherflags.names)
        self.set( **otherflags.subset( *names))

    def copy(self):
        return self.__class__(**self.d)

    def copy_update(self, **kw):
        f = self.copy()
        f.set(**kw)
        return f

    def copy_sync(self, otherflags):
        f = self.copy()
        f.sync(otherflags)
        return f


        



class FlagsFactory(object):

    @classmethod
    def _get_type(cls, size):
        _type = None
        if size == 8:
            _type = 'B'
        elif size == 16:
            _type = 'H'
        elif size == 32:
            _type = 'I'
        elif size == 64:
            _type = 'Q'
        else:
            msg = 'size must be one of 8, 16, 32, 64'
            raise FlagsFactoryException(msg)
        return _type
        
    @classmethod
    def _property_get(cls, name):
        def _get(self):
            flagbit = getattr(self, 'F_'+name.upper())
            return bool(self._flags & flagbit)
        return property(_get)

    @classmethod
    def _method_set_name(cls, name):
        def _set(self, value):
            self.set(name, value)
        return _set

    def __new__(cls, classname, size, names_defaults):
        d = {} 
        _flag_names = []
        _flag_names_defaults = []
        _type = ''
        _flagbit = {}

        d['_FlagsFactory_args'] = (classname, size, names_defaults)

        for (name,val) in names_defaults:
            name = name.lower()
            val = bool(val)
            _flag_names.append(name)
            _flag_names_defaults.append((name, val))
        if len(set(_flag_names)) < len(_flag_names):
            msg = 'flag names not unique'
            raise FlagFactoryException(msg)
        d['_flag_names'] = _flag_names
        d['_flag_names_defaults'] = _flag_names_defaults

        if size < len(_flag_names):
            msg = 'number of flag names is larger than size (%d)' % size
            raise FlagsFactoryException(msg)
        d['_type'] = cls._get_type(size)
        d['_size'] = size

        for (i,name) in enumerate(_flag_names):
            val = 1 << i
            _flagbit[name]       = val
            d['F_'+name.upper()] = val
            d['set_'+name]       = cls._method_set_name(name)
            d[name]              = cls._property_get(name)
        d['_flagbit'] = _flagbit

        _flags = 0L
        for (name,default) in _flag_names_defaults:
            if default:
                _flags |= _flagbit[name]
        d['_flags'] = _flags

        return type(classname, (FlagsBase,), d)



import unittest
class Test_FlagsFactory(unittest.TestCase):
    def test_test(self):
        assert 1==1

    def test1(self):
        X = FlagsFactory('X', 8, [
            ('asd', True),
            ('qwe', False),
            ('foo', False),
            ('bar', False),
        ])
        x = X()
        assert x.asd
        assert not x.qwe
        assert not x.foo
        assert not x.bar
        x2 = X(qwe=True)
        assert x2.asd
        assert x2.qwe
        assert not x2.foo
        assert not x2.bar

        x.set('asd', False)
        assert not x.asd
        x.set('asd', True)
        assert x.asd

        x.set_asd(False)
        assert not x.asd
        x.set_asd(True)
        assert x.asd

        x.set(**dict(
            asd=0,
            qwe=0,
            foo=0,
            bar=0,
        ))
        assert x.d == dict(
            asd=False,
            qwe=False,
            foo=False,
            bar=False,
        )

        x.set(**dict(
            asd=1,
            qwe=1,
            foo=1,
            bar=1,
        ))
        assert type(x) is type(X())
        assert x['asd'] == True
        assert x['qwe'] == True
        assert type(x.d) is type({})
        assert x.d['asd'] == True
        assert x.d['qwe'] == True

        assert x.subset('foo', 'bar') == dict(foo=True,bar=True)
        assert x.names == tuple(['asd','qwe','foo','bar'])

        W = FlagsFactory('W', 8, [
            ('asd',   False),
            ('blurg', False),
        ])
        w = W()
        w.sync(x)
        assert w.d == dict(asd=True, blurg=False)


def _test():
    import doctest
    import unittest
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()

