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


from tickets import SecureTicket
from tickets import SecureTicketPublicFlags
from tickets import SecureTicketFlags
from tickets import SecureTicketService
from tickets import SecureTicketException
from tickets import InvalidTicketException

from tickets.tests.utils import flip_bit

import unittest
import random
import uuid
import zlib
import datetime

try:
    from sets import Set as set
except ImportError:
    pass


def debug_print_ticket(ticket):
    print ticket
    for name in ('_bytes', 'prefix', 'hash', 'salt', 'raw_public_flags', 'raw_flags',
                'raw_valid_until', 'raw_data'):
        value =  getattr(ticket, name)
        print len(value), name, repr(value)



class Test_new_SecureTicketService(unittest.TestCase):
    def _test_test(self):
            assert 1==2

    def setUp(self):
        pass

    def test_various_combinations_and_bitflips(self):
        key_variations = [
            SecureTicketService.create_random_key() for _ in xrange(2)
        ]
        kw_variations = [
            dict(encrypt=0, serialize=0, compress=0),
            dict(encrypt=0, serialize=0, compress=1),
            dict(encrypt=0, serialize=1, compress=0),
            dict(encrypt=0, serialize=1, compress=1),
            dict(encrypt=1, serialize=0, compress=0),
            dict(encrypt=1, serialize=0, compress=1),
            dict(encrypt=1, serialize=1, compress=0),
            dict(encrypt=1, serialize=1, compress=1),
        ]
        entropy_variations = [
            'E'*i for i in (0, 1, 15, 16, 17)
        ]
        data_variations = [
            'D'*i for i in (0, 1, 15, 16, 17)
        ]

        for key in key_variations:
            for kw in kw_variations:
                for entropy in entropy_variations:
                    for data in data_variations:
                        #print kw

                        #print 'data, entropy:', repr(entropy), repr(data)

                        sts = SecureTicketService(key, **kw)

                        t1 = sts.create_ticket(data, entropy)
                        t2 = SecureTicket.fromstring(t1.tostring())
                        t3 = SecureTicket.frombase64(t2.tobase64())

                        assert sts.validate_ticket(t1, entropy)
                        if not t1.is_encrypted:
                            assert t1.data == data
                        assert sts(t1).data == data

                        assert sts.validate_ticket(t2, entropy)
                        if not t2.is_encrypted:
                            assert t2.data == data
                        assert sts(t2).data == data

                        assert sts.validate_ticket(t3, entropy)
                        if not t3.is_encrypted:
                            assert t3.data == data
                        assert sts(t3).data == data

                        s = t1.tostring()
                        flip_pos = random.randint(0, len(s)*8-1)
                        t = flip_bit(s, flip_pos)
                        assert s != t
                        try:
                            t4 = SecureTicket.fromstring(t)
                            assert not sts.validate_ticket(t4, entropy)
                        except InvalidTicketException:
                            pass

                        u = flip_bit(t, flip_pos)
                        t5 = SecureTicket.fromstring(u)
                        assert sts.validate_ticket(t5, entropy)

                        #if not sts(ticket).data == data:
                        #    print 'FAIL data==data', ticket


    def test_serialization(self):
        key_variations = [
            SecureTicketService.create_random_key() for _ in xrange(2)
        ]
        kw_variations = [
            dict(encrypt=0, serialize=1, compress=0),
            dict(encrypt=0, serialize=1, compress=1),
            dict(encrypt=1, serialize=1, compress=0),
            dict(encrypt=1, serialize=1, compress=1),
        ]
        entropy_variations = [
            '', 'EEEEEEEEEEE'
        ]
        data_variations = [
            None,
            [],
            (),
            dict(),
            1,
            2L,
            3.14,
            set(),
            [
                123,
                [
                    dict(asd=123, qwe=456),
                    ['foo', ('bar','qwe')],
                    set(['robot', u'brains', None])
                ]
            ]
        ]
        for key in key_variations:
            for entropy in entropy_variations:
                for data in data_variations:
                    for kw in kw_variations:
                        sts = SecureTicketService(key, **kw)
                        t1 = sts.create_ticket(data, entropy)
                        assert sts.validate_ticket(t1, entropy)
                        if not t1.is_encrypted:
                            assert t1.data == data
                        assert sts(t1).data == data
                        #if t1.ticket_len > 100:
                        #    print '--------------------------------------'
                        #    print t1.ticket_len, kw
                        #    print data


    def test_large_tickets(self):
        # these take time
        kw_variations = [
            #dict(encrypt=0, serialize=0, compress=0),
            #dict(encrypt=0, serialize=0, compress=1),
            #dict(encrypt=0, serialize=1, compress=0),
            #dict(encrypt=0, serialize=1, compress=1),
            #dict(encrypt=1, serialize=0, compress=0),
            #dict(encrypt=1, serialize=0, compress=1),
            #dict(encrypt=1, serialize=1, compress=0),
            dict(encrypt=1, serialize=1, compress=1),
        ]
        for kw in kw_variations:
            from tickets.log import debug, info
            key = SecureTicketService.create_random_key()
            sts = SecureTicketService(key, **kw)
            data = 'D' * (10**6)
            ticket = sts.create_ticket(data, 'asdasd')
            if not kw['encrypt']:
                assert ticket.data == data
            assert sts(ticket).data == data
            assert sts.validate_ticket(ticket, 'asdasd')
            assert not sts.validate_ticket(ticket, 'asdasd.')
    

class Test_SecureTicket(unittest.TestCase):
    def _test_test(self):
            assert 1==1

    def setUp(self):
        pass

    def test_properties_and_serialization(self):
        salt_variations = [
            uuid.uuid4().bytes[:SecureTicket.SALT_LEN] for _ in xrange(4)
        ]
        hash_variations = [
            (uuid.uuid4().bytes*2)[:SecureTicket.HASH_LEN] for _ in xrange(4)
        ]
        public_flags_variations = [
            SecureTicketPublicFlags(encrypt=0),
            #SecureTicketPublicFlags(encrypt=1),
        ]
        flags_variations = [
            SecureTicketFlags(serialize=0, compress=0)
        ]
        valid_until_variations = [
            random.randint(0, 0xffffffff) for _ in xrange(4)
        ]
        data_variations = [
            'X'*i for i in xrange(20)
        ]
        for salt in salt_variations:
            for hash_ in hash_variations:
                for public_flags in public_flags_variations:
                    for flags in flags_variations:
                        for valid_until in valid_until_variations:
                            for data in data_variations:
                                ticket = SecureTicket()._load_from_parts(
                                    hash_,
                                    salt,
                                    public_flags, 
                                    flags,
                                    valid_until,
                                    data
                                )
                                if ticket.raw_valid_until == '':
                                    print 'BROKEN', repr(valid_until), valid_until
                                    debug_print_ticket(ticket)
                                    raise Exception
                                assert len(ticket.raw_valid_until) == 4
                                assert ticket.salt         == salt
                                assert ticket.hash         == hash_
                                #
                                # SecureTicketFlags unpacks into new instances.
                                #
                                assert ticket.flags._serialize() == flags._serialize()
                                assert ticket.valid_until        == valid_until 
                                assert ticket.data               == data



class Test_SecureTicketService(unittest.TestCase):
    def _test_test(self):
        assert 1==1

    def setUp(self):
        self.sts = SecureTicketService('some key')
        self.sts_other = SecureTicketService('other key')

    def test_validate(self):
        '''
            Validate tickets created from all combinations of random keys of length 1 to 16 bytes,
            entropy of length 0 to 16 and data of length 1 to 16.

            Assert validation failure for each successful validation, when using a key which
            differs by one bit from the correct key.

        '''
        key_variations = [
            uuid.uuid4().bytes[:i] for i in xrange(1,16)
        ]
        entropy_variations = [
            uuid.uuid4().bytes[:i] for i in xrange(8)
        ]
        data_variations = [
            'A'*i for i in xrange(16,64)
        ]
        key_flip_bit = 0
        for key in key_variations:
            sts = SecureTicketService(key)
            stsfail = SecureTicketService(
                flip_bit(key, key_flip_bit % (len(key)*8))
            )
            key_flip_bit += 7

            for entropy in entropy_variations:
                for data in data_variations:
                    assert not data is None
                    ticket = sts.create_ticket(data, entropy)
                    assert sts.validate_ticket(ticket, entropy)
                    assert not stsfail.validate_ticket(ticket, entropy)

    def test_data(self):
        key_variations = [
            uuid.uuid4().bytes[:i] for i in xrange(1,16)
        ]
        entropy_variations = [
            uuid.uuid4().bytes[:i] for i in xrange(8)
        ]
        data_variations = [
            'A'*i for i in xrange(16,33)
        ]
        key_flip_bit = 0
        for key in key_variations:
            sts = SecureTicketService(key)
            stsfail = SecureTicketService(
                flip_bit(key, key_flip_bit % (len(key)*8))
            )
            key_flip_bit += 7

            for entropy in entropy_variations:
                for data in data_variations:
                    assert not data is None
                    ticket = sts.create_ticket(data, entropy)
                    assert sts.validate_ticket(ticket, entropy)
                    assert sts(ticket).data == data

                



def choffset(self, string, offset, val):
    import array
    arr = array.array('c', string)
    newval = chr( (ord(arr[offset])+val) % 256 )
    arr[offset] = newval
    return arr.tostring()



__all__ = []
for (name,val) in locals().copy().iteritems():
    try:
        if issubclass(val, unittest.TestCase):
            __all__.append(name)
    except:
        pass


def _test():
    unittest.main()

if __name__ == "__main__":
    _test()

