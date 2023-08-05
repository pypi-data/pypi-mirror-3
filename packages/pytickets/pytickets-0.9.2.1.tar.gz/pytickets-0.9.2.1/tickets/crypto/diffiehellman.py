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
'''
    DiffieHellman, DiffieHellmanClient, DiffieHellmanServer
    =======================================================
    *DiffieHellman* implements the Diffie Hellman key exchange algorithm.
    Variable names in the implementation match those from
    *Diffie-Hellman Key Agreement Method (RFC 2631)*, but in each method *xa* and
    *ya* are used for the secret and the exposed key parts in *self* while *xb*
    (which is never seen) and *yb* is the key parts of the other party.

    >>> a = DiffieHellman(psize=2048) # prime size defaults to 1536
    >>> b = DiffieHellman(psize=2048)
    >>> ZZa = a.calc_ZZ(b.ya) # ZZ is the negotiated secret
    >>> ZZb = b.calc_ZZ(a.ya)
    >>> ZZa == ZZb
    True
    >>> type(ZZa)
    <type 'long'>
    >>> strZZ = tickets.crypto.util.long2str(ZZa)
    >>> type(strZZ)
    <type 'str'>

    *DiffieHellmanClient* and *DiffieHellmanServer* implements a protocol by
    which two parties are able to perform a Diffie Hellman key exchange and
    to verify that the other party has successfully derived the same secret
    key.

    The protocol follows the common Diffie Hellman scheme, but additionally
    includes generation and validation of SHA256-HMAC digests, using the
    negotiated key, of some of the negotiation messages. This is in a sense
    similar to the well known TCP three way handshake.

    >>> c = DiffieHellmanClient(asize=256) # asize should be 256 for aes128
    >>> s = DiffieHellmanServer() # will adapt to client in 'hello' phase
    >>> A = c.client_hello()
    >>> B = s.server_hello(A)
    >>> C = c.client_verify(B)
    >>> s.server_verify(C)
    True
    >>> c.negotiated_key == s.negotiated_key
    True
    >>> type(c.negotiated_key)
    <type 'str'>

'''


__all__ = [
    'DiffieHellmanException',
    'DiffieHellman',
    'DiffieHellmanHandshake',
]

import tickets.crypto.rfc3526
import tickets.crypto.util
import tickets.bytemapper

import struct
import uuid
import hmac
import hashlib

import unittest
import doctest




class NotImplemented(Exception): pass

class DiffieHellmanException(Exception): pass



class DiffieHellman(object):

    def __init__(self, asize=256, psize=1536, p=None, g=None):
        self.asize = asize
        self.psize = psize
        if p or g:
            assert p and g # specify none or both
        else:
            p, g = tickets.crypto.rfc3526.modp[psize]
        self.p, self.g = p, g
        self.xa = self._produce_secret()
        self.ya = self._calc_ya()

    def _produce_secret(self):
        return tickets.crypto.util.produce_random_long(self.asize)

    def _calc_ya(self):
        return tickets.crypto.util.powmod(self.g, self.xa, self.p)

    def calc_ZZ(self, yb):
        return tickets.crypto.util.powmod(yb, self.xa, self.p)
        


class DiffieHellmanHandshake(object):

    MAGIC_PREFIX = '\xd1\xff\x1e\x11'

    def __init__(self, asize=256, psize=1536):
        self._asize = asize
        self._psize = psize
        self._dh = None
        self._client_hello_called = False
        self._server_hello_called = False
        self._client_verify_called = False

    def _verify_prefix(self, msg):
        assert msg[:4] == self.MAGIC_PREFIX
        return msg[4:]

    def _hmac(self, key, msg):
        if type(key) in (long, int):
            key = tickets.crypto.util.long2str(key)
        return hmac.new(key, msg, hashlib.sha256).digest()

    negotiated_key = property(lambda self : self._strZZ) #str
    ZZ             = property(lambda self : self._ZZ) #long



class DiffieHellmanClient(DiffieHellmanHandshake):
    def _client_hello(self, asize, psize, g, p, ya):
        '''
            bytes    name
            =====    ==== 
            2        asize
            2        psize
            2        g
            psize/8  p
            psize/8  ya
        '''
        msg = ''
        msg += struct.pack('H', asize)
        msg += struct.pack('H', psize)
        msg += struct.pack('H', g)
        msg += tickets.crypto.util.long2str(p, psize/8)
        msg += tickets.crypto.util.long2str(ya, psize/8)
        return self.MAGIC_PREFIX + msg

    def _parse_server_hello(self, msg):
        psize = self._dh.psize
        yb    = tickets.crypto.util.str2long(msg[:psize/8])
        h     = msg[psize/8:]
        assert len(h) == 32
        return (yb, h)

    def _client_verify(self, h, ZZ):
        '''
            bytes    name
            =====    ==== 
            32       server's hash of its ya
            32       client's hash of server's hash
        '''
        return self.MAGIC_PREFIX + h + self._hmac(ZZ, h)

    #
    # public
    #
    def client_hello(self):
        self._dh = dh = DiffieHellman(self._asize, self._psize)
        return self._client_hello(self._asize, self._psize, dh.g, dh.p, dh.ya)

    def client_verify(self, msg):
        msg = self._verify_prefix(msg)
        (yb, h) = self._parse_server_hello(msg)
        self._ZZ = ZZ = self._dh.calc_ZZ(yb)
        self._strZZ = tickets.crypto.util.long2str(ZZ)
        assert h == self._hmac(ZZ, msg[:-32])
        return self._client_verify(h, ZZ)



class DiffieHellmanServer(DiffieHellmanHandshake):

    def _parse_client_hello(self, msg):
        asize = struct.unpack('H', msg[0:2])[0]
        psize = struct.unpack('H', msg[2:4])[0]
        g     = struct.unpack('H', msg[4:6])[0]
        p     = tickets.crypto.util.str2long(msg[6:6+psize/8])
        _yb   = msg[6+psize/8:]
        assert len(_yb) == psize/8
        yb    = tickets.crypto.util.str2long(_yb)
        return (asize, psize, g, p, yb)

    def _server_hello(self, psize, ya, ZZ):
        '''
            bytes    name
            =====    ==== 
            psize/8  ya
            32       hash of ya
        '''
        msg = ''
        msg += tickets.crypto.util.long2str(ya, psize/8)
        msg += self._hmac(ZZ, msg)
        return self.MAGIC_PREFIX + msg

    def _parse_client_verify(self, msg):
        assert len(msg) == 64
        hya, h = msg[:32], msg[32:]
        return (hya, h)

    #
    # public
    #
    def server_hello(self, msg):
        msg = self._verify_prefix(msg)
        (asize, psize, g, p, yb) = self._parse_client_hello(msg)
        self._dh = dh = DiffieHellman(asize, psize, p=p, g=g)
        self._ZZ = ZZ = dh.calc_ZZ(yb)
        self._strZZ = tickets.crypto.util.long2str(ZZ)
        return self._server_hello(psize, dh.ya, ZZ)

    def server_verify(self, msg):
        msg = self._verify_prefix(msg)
        (hya, h) = self._parse_client_verify(msg)
        str_ya = tickets.crypto.util.long2str(self._dh.ya)
        assert hya == self._hmac(self._ZZ, str_ya)
        assert h   == self._hmac(self._ZZ, hya)
        return True


        



class Test_DiffieHellman(unittest.TestCase):
    def _test_test(self):
        assert 1==2

    def verify_secrets(self, u, w):
        uZZ = u.calc_ZZ(w.ya)
        wZZ = w.calc_ZZ(u.ya)
        self.assertEqual(uZZ, wZZ)

    def test1(self):
        p, g = 7, 3
        u = DiffieHellman(p=p, g=g)
        w = DiffieHellman(p=p, g=g)
        self.verify_secrets(u, w)
        for (psize, pg) in tickets.crypto.rfc3526.modp.iteritems():
            if 1:
                u = DiffieHellman(psize)
                w = DiffieHellman(psize)
                self.verify_secrets(u, w)
            if 1:
                p, g = pg
                u = DiffieHellman(p=p, g=g)
                w = DiffieHellman(p=p, g=g)
                self.verify_secrets(u, w)



class Test_DiffieHellmanHandshake(unittest.TestCase):
    def _test_test(self):
        assert 1==2

    def test1(self):
        c = DiffieHellmanClient()
        s = DiffieHellmanServer()

        import time
        t = time.time()
        count = 10
        for i in xrange(count):
            s.server_verify(
                c.client_verify(
                    s.server_hello(
                        c.client_hello()
                    )
                )
            )
        #
        # about 60 complete key negotiations per second on my macbook pro.
        #
        #print count / (time.time() - t)



def _test():
    doctest.testmod()
    unittest.main()


if __name__ == '__main__':
    _test()

