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


import uuid
import struct

class NotImplemented(Exception): pass



class BaseDiffieHellman(object):

    SECRET_SIZE = 2

    def _produce_random_string(self, nchars):
        s = ''
        while len(s) < nchars:
            s += uuid.uuid4().bytes
        return s[:nchars]

    def _produce_secret(self):
        val = 0L
        s = self._produce_random_string(self.SECRET_SIZE)
        n = 0
        while len(s):
            t = s[-4:]
            s = s[:-4]
            if len(t) == 2:
                val += 256**n * struct.unpack('H', t)[0]
            elif len(t) == 4:
                val += 256**n * struct.unpack('I', t)[0]
            else:
                raise Exception('bad len: {0}'.format(len(t)))
            n += 4
        return val
        

class DiffieHellman_a(BaseDiffieHellman):
    def __init__(self, p, g):
        self.p, self.g = p, g
        self.a = self._produce_secret()

    def get_pgA(self):
        p = self.p
        g = self.g
        a = self.a
        #
        A = g**a % p
        return (p, g, A)

    def set_B(self, B):
        self.B = B

    def get_s(self):
        B = self.B
        a = self.a
        p = self.p
        #
        s = B**a % p
        return s


class DiffieHellman_b(BaseDiffieHellman):
    def __init__(self):
        self.b = self._produce_secret()

    def set_pgA(self, p, g, A):
        self.p, self.g, self.A = p, g, A

    def get_B(self):
        p = self.p
        g = self.g
        b = self.b
        #
        B = g**b % p
        return B
        
    def get_s(self):
        A = self.A
        b = self.b
        p = self.p
        #
        s = A**b % p
        return s
        


import unittest
class Test_DiffieHellman(unittest.TestCase):
    def _test_test(self):
        assert 1==2

    def test1(self):

        dha = DiffieHellman_a(7, 3)
        dhb = DiffieHellman_b()

        dhb.set_pgA( *dha.get_pgA()) 
        dha.set_B( dhb.get_B())

        #print dha.a
        #print dhb.b
        #print dha.get_s()

        assert dha.get_s() == dhb.get_s()



def _test():
    unittest.main()

if __name__ == '__main__':
    _test()

