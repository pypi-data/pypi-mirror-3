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
    'BaseAES',
    'AES',
]

import hashlib
import unittest
import uuid



class BaseAES:
    '''
    BaseAES provides a high-level interface to encryption using AES from pyCrypto.

        encrypt(iv, plaintext)
        decrypt(iv, ciphertext)

        Encrypt/decrypt text using AES128 CBC and an IV structure specific
        to SimpleAES. An 8-byte salt must be supplied in each call to
        encrypt().

    '''
    def __init__(self, key):
        import hashlib
        from Crypto.Cipher import AES
        self._AES = AES
        self._key = self._fix_key(key)

    def _new_aes(self, iv):
        iv = iv[:16]
        assert len(iv) == 16
        return self._AES.new(self._key, self._AES.MODE_CBC, iv)

    def _fix_key(self, key):
        while len(key) < 32:
            key += hashlib.sha256(key).digest()
        key = key[:32]
        return key

    @classmethod
    def new_key(cls):
        '''
            Create a key suitable for AES encryption.
        '''
        return uuid.uuid4().bytes + uuid.uuid4().bytes

    @classmethod
    def new_iv(cls):
        '''
            Create a 16-byte IV (128 bits) suitable as an initialization vector
            for AES128 CBC encryption.
        '''
        return uuid.uuid4().bytes

    def iter_encrypt_blocks(self, iv, plaintext):
        aes = self._new_aes(iv)
        while plaintext:
            block = plaintext[:16] 
            if len(block) < 16:
                block += '\x00' * (16-len(block))
            block = aes.encrypt(block)
            yield block
            plaintext = plaintext[16:]
        
    def iter_decrypt_blocks(self, iv, ciphertext):
        aes = self._new_aes(iv)
        while ciphertext:
            block = ciphertext[:16]
            block = aes.decrypt(block)
            yield block
            ciphertext = ciphertext[16:]

    def encrypt(self, iv, plaintext):
        '''
            Encrypt 'plaintext' using AES128 CBC.

            Plaintext is padded with '\x00'-bytes if necessary to make the
            last block 16 bytes wide. This means that you have to keep track
            of plaintext's actual length.
        '''
        ciphertext = ''
        for block in self.iter_encrypt_blocks(iv, plaintext):
            ciphertext += block
        return ciphertext

    def decrypt(self, iv, ciphertext):
        '''
            Decrypt 'ciphertext' using AES128 CBC.

            The length of the returned plaintext is always a multiple of the
            block-size which is 16 for AES128.
        '''
        plaintext = ''
        for block in self.iter_decrypt_blocks(iv, ciphertext):
            plaintext += block
        return plaintext


class AES(BaseAES):
    def decrypt_first_block(self, iv, ciphertext):
        assert len(ciphertext) >= 16
        return self._new_aes(iv).decrypt(ciphertext[:16])


class Test_BaseAES(unittest.TestCase):
    def test_test(self):
        assert 1==1

    def test_encrypt(self):
        plaintext = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        plaintext += plaintext.lower()
        plaintext += '0123456789'
        iv = uuid.uuid4().bytes
        iv2 = uuid.uuid4().bytes
        key = uuid.uuid4().bytes 
        aes = BaseAES(key)
        ciphertext = aes.encrypt(iv, plaintext)
        assert len(plaintext)  == 62
        assert len(ciphertext) == 64
        assert ciphertext.find('12345') == -1
        #print repr(aes.decrypt(iv, ciphertext))
        assert aes.decrypt(iv, ciphertext)[:-2] == plaintext
        assert aes.decrypt(iv2, ciphertext)[:-2] != plaintext
        




def _test():
    unittest.main()

if __name__ == '__main__':
    _test()

