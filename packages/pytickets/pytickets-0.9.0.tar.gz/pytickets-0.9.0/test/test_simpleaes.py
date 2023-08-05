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
    'Test_SimpleAES',
]


import unittest
import sys
#from os.path import abspath, dirname
#sys.path.insert(0, 
#    dirname(dirname(abspath(__file__)))
#)


from tickets.utils import SimpleAES


class Test_SimpleAES(unittest.TestCase):
    def test_test(self):
        assert 1==1
    
    def randstring(self, n):
        import random
        return ''.join(chr(random.randint(0,255)) for _ in xrange(n))

    def test_encrypt_decrypt_various_lengths(self):
        '''
            Test SimepleAES encrypt/decrypt on random strings of len 0 to 1023
        '''
        import uuid
        saes = SimpleAES(uuid.uuid4().bytes)
        for n in xrange(1024):
            text = self.randstring(n)
            salt1 = uuid.uuid4().bytes
            salt2 = uuid.uuid4().bytes
            ciphertext = saes.encrypt(salt1, text)
            assert ciphertext != saes.encrypt(salt2, text)
            assert text == saes.decrypt(salt1, ciphertext)
        

if __name__ == "__main__":
    unittest.main()

