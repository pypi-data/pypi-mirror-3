#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
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
    'ByteMapperFactory'
]




class BaseByteMapper(object):

    @classmethod
    def _join_strings(cls, names_values):
        def string_start_offset(name):
            return getattr(cls, name.upper()+'_OFFSET')
        sorted_strings = [
            names_values[name] for name in
                sorted(names_values, key=string_start_offset)
        ]
        return ''.join(sorted_strings)

    @classmethod
    def _serialize_join_strings(cls, names_values, **kw):
        _names_values = {}
        for (name,val) in names_values.iteritems():
            serialize = getattr(cls, '_serialize_'+name)
            val = serialize(val, **kw)
            assert type(val) is str
            _names_values[name] = val
        names_values = _names_values
        return cls._join_strings(names_values)

    @classmethod
    def _split_strings(cls, plaintext, *names):
        '''
            beware: no alerts if plaintext is too small
        '''
        def string_start_offset(name):
            return getattr(cls, name.upper()+'_OFFSET')
        sorted_strings = []
        for name in sorted(names, key=string_start_offset):
            len_ = getattr(cls, name.upper()+'_LEN')
            s = plaintext[:len_]
            sorted_strings.append(s)
            plaintext = plaintext[len_:]
        return tuple(sorted_strings)

    @classmethod
    def _split_deserialize_strings(cls, plaintext, names):
        '''
            beware: no alerts if plaintext is too small
        '''
        def string_start_offset(name):
            return getattr(cls, name.upper()+'_OFFSET')
        sorted_values = []
        for name in sorted(names, key=string_start_offset):
            len_ = getattr(cls, name.upper()+'_LEN')
            deserialize = getattr(cls, '_deserialize_'+name)
            s = deserialize(plaintext[:len_])
            sorted_values.append(s)
            plaintext = plaintext[len_:]
        return tuple(sorted_values)




class ByteMapperFactory(object):
    '''
        ByteMapperFactory creates new classes able to parse custom byte ranges
        from attribute _bytes. Parsing is done by slicing. Attribute _bytes can
        be of any sliceable type but must be explicitly set in instances!

        Make sure to declare _bytes, preferrably in __init__() of inheriting classes:

        >>> _MyBM = ByteMapperFactory('_MyBM', [ (3,'asd'), (3,'qwe') ])
        >>> class MyBM(_MyBM):
        ...     def __init__(self):
        ...         super(MyBM, self).__init__()
        ...         self._bytes = [1,2,3,4,5,6]
        ...
        >>> a = MyBM()
        >>> assert a.asd == [1,2,3]
        >>> assert a.qwe == [4,5,6]
        >>> assert a.QWE_OFFSET == 3

    '''
    @classmethod
    def classmethod_parse(cls, start, end):
        @classmethod
        def parse(cls, b):
            return b[start : end]
        return parse

    @classmethod
    def classmethod_serialize(cls):
        @classmethod
        def serialize(self, val, **kw):
            return val
        return serialize

    @classmethod
    def classmethod_deserialize(cls):
        @classmethod
        def deserialize(self, val, **kw):
            return val
        return deserialize

    @classmethod
    def property_get(cls, name):
        @property
        def getter(self):
            parse = getattr(self.__class__, '_parse_'+name)
            deserialize = getattr(self.__class__, '_deserialize_'+name)
            val = parse(self._bytes)
            return deserialize(val)
        return getter


    def __new__(cls, classname, sizes_names):
        d = {}
        d['_ByteMapperFactory_args'] = (classname, sizes_names)
        d['_offsets'] = {}
        offset = 0
        for tup in sizes_names:
            try:
                size, name, docs = tup
            except ValueError:
                size, name = tup
                docs = ''

            start, end = offset, offset+size
            #
            # class attributes
            #
            d['_offsets'][name]       = (start, end)
            d[name.upper()+'_OFFSET'] = start
            d[name.upper()+'_LEN']    = size
            d['OFFSET_'+name.upper()] = start
            #
            # classmethods
            #
            d['_parse_'+name]               = cls.classmethod_parse(start, end)
            d['_serialize_'+name]           = cls.classmethod_serialize()
            d['_deserialize_'+name]         = cls.classmethod_deserialize()
            #
            # properties
            #
            d[name]                   = cls.property_get(name)
            offset += size
        d['_bytes_len'] = offset
        return type(classname, (BaseByteMapper,), d)




import unittest
class Test_ByteMapperFactory(unittest.TestCase):
    def test_test(self):
        assert 1==1

    def test1(self):
        X = ByteMapperFactory('X', [
            (2, 'asd'),
            (2, 'qwe'),
            (4, 'foo'),
            (4, 'bar'),
        ])

        class Y(X):
            def __init__(self):
                super(Y, self).__init__()
                self._bytes = range(self._bytes_len)

        y = Y()
        assert y.asd == [0,1]
        assert y.qwe == [2,3]
        assert y.foo == [4,5,6,7]
        assert y.bar == [8,9,10,11]

        class Z(Y):
            @classmethod
            def _deserialize_asd(cls, val):
                return [str(i) for i in val]

        z = Z()
        assert z.asd == ['0', '1']
        assert z.qwe == [2, 3]

    def test_join_strings(self):
        X = ByteMapperFactory('X', [
            (2, 'asd'),
            (2, 'qwe'),
            (4, 'foo'),
            (4, 'bar'),
        ])
        res = X._join_strings(dict(qwe='QWE', bar='BAR', asd='ASD'))
        assert res == 'ASDQWEBAR'

        class Y(X):
            @classmethod
            def _serialize_bar(cls, val):
                return val+'rrr'
        res = Y._serialize_join_strings(dict(qwe='QWE', bar='BAR', asd='ASD'))
        assert res == 'ASDQWEBARrrr'


        


def _test():
    import doctest
    import unittest
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()

