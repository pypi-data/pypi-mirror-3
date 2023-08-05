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



class Interface(object): pass
class NotImplementedException(Exception): pass


class ISerializable(Interface):
    def serialize(self):
        raise NotImplementedException('implement serialize()')
        
    @classmethod
    def deserialize(self, b):
        raise NotImplementedException('implement @classmethod deserialize()')



class Serializer(object):
    '''
        Separate Serializer class, not indended to be subclassed by classes
        wishing to be serialized. Serializer instances are intended to be used
        by MultiSerializable instances.
    '''

    def serialize(self, val):
        raise NotImplementedException('implement serialize()')
        
    def deserialize(self, val):
        raise NotImplementedException('implement @classmethod deserialize()')



class MultiSerializable(ISerializable):

    _serializers = []

    @classmethod
    def add_serializer(cls, serializer):
        cls._serializers.append(serializer)

    def serialize(self):
        val = self
        for serializer in self._serializers:
            val = serializer.serialize(val)
        return val

    @classmethod
    def deserialize(cls, val):
        serializers = cls._serializers
        for i in xrange(len(serializers)-1, -1, -1):
            val = serializers[i].deserialize(val)
        return cls(val)
    
    

import doctest
import unittest
class Test_MultiSerializable(unittest.TestCase):

    def test_test(self):
        assert 1==1

    def test1(self):

        class MS(list, MultiSerializable):
            pass

        class AddOne(Serializer):
            def serialize(self, val):
                lst = val[:]
                for i in xrange(len(lst)):
                    lst[i] += 1
                return lst
            def deserialize(self, val):
                lst = val[:]
                for i in xrange(len(lst)):
                    lst[i] -= 1
                return lst

        class AddTwo(Serializer):
            def serialize(self, val):
                lst = val[:]
                for i in xrange(len(lst)):
                    lst[i] += 2
                return lst
            def deserialize(self, val):
                lst = val[:]
                for i in xrange(len(lst)):
                    lst[i] -= 2
                return lst

        MS.add_serializer(AddOne())
        MS.add_serializer(AddTwo())

        ms = MS([0,1,2])
        assert len(ms) == 3

        ms = ms.serialize()
        assert ms == [3,4,5]
        ms = MS.deserialize(ms)
        assert ms == [0,1,2]
        


def _test():
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()

