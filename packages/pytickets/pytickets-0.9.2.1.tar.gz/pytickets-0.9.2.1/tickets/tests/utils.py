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


import array
import unittest

__all__ = [
    'flip_bit',
]



def flip_bit(s, bitpos):
    arr = array.array('c', s)
    bytepos = bitpos / 8
    bitnum  = bitpos % 8
    ch = ord(arr[bytepos])
    ch ^= 1 << bitnum
    arr[bytepos] = chr(ch)
    return arr.tostring()



class Test_utils(unittest.TestCase):
    def test_test(self):
        assert 1==1

    def setUp(self):
        pass

    def test_flip_bit(self):
        s = '\xf0\x0f'
        assert flip_bit(s, 0) == '\xf1\x0f'
        assert flip_bit(s, 1) == '\xf2\x0f'
        assert flip_bit(s, 2) == '\xf4\x0f'
        assert flip_bit(s, 7) == '\x70\x0f'
        assert flip_bit(s, 8+0) == '\xf0\x0e'
        assert flip_bit(s, 8+1) == '\xf0\x0d'
        assert flip_bit(s, 8+2) == '\xf0\x0b'
        assert flip_bit(s, 8+7) == '\xf0\x8f'


def _test():
    import unittest
    unittest.main()

if __name__ == "__main__":
    _test()

