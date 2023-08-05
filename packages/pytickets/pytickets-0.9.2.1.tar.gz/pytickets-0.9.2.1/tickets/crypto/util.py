#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = [
    'powmod',
    'str2long',
    'hexstr2long',
    'produce_random_string',
    'produce_random_long',
]


import uuid
import struct
import hashlib

import unittest


def powmod(b, e, m):
    '''
        returns b**e % m
    '''
    val = 1
    i = 0
    w = b
    while (e >> i):
        if (e >> i) & 1:
            val = (val * w) % m
        w = w**2 % m
        i += 1
    return val


def str2long(s):
    val = 0L
    n = 0
    while len(s):
        t = s[-4:]
        s = s[:-4]
        while len(t) < 4:
            t = '\x00' + t
        I = struct.unpack('>I', t)[0]
        val += I << (8*n)
        n += 4
    return val

def long2str(val, padlen=None):
    s = ''
    while val:
        I = val & 0xffffffffL
        val = val >> (4*8)
        t = struct.pack('>I', I)
        s = t + s
    if padlen and len(s) < padlen:
        n = padlen - len(s)
        s = '\x00'*n + s
    return s
        

def hexstr2long(s):
    s = ''.join(s.split()).decode('hex')
    return str2long(s)


def produce_random_string(nchars):
    '''
        slow due to SHA256-hashing of every 32 bytes
    '''
    s = ''
    while len(s) < nchars:
        r = uuid.uuid4().bytes
        h = hashlib.sha256(r).digest()
        s += h
    return s[:nchars]


def produce_random_long(nbits):
    assert (nbits % 8) == 0
    val = 0L
    s = produce_random_string(nbits / 8)
    n = 0
    while len(s):
        t = s[-4:]
        s = s[:-4]
        while len(t) < 4:
            t = '\x00' + t
        chunk = struct.unpack('>I', t)[0]
        val += chunk << (8*n)
        n += 4
    return val



class Test_util(unittest.TestCase):
    def _test_test(self):
        assert 1==2

    def test_str2long_long2str(self):
        ss = [uuid.uuid4().bytes[:i] for i in xrange(1,32)]
        for s in ss:
            while (len(s) % 4):
                s = '\x00' + s
            assert s == long2str(str2long(s))
        


def _test():
    unittest.main()

if __name__ == "__main__":
    _test()

