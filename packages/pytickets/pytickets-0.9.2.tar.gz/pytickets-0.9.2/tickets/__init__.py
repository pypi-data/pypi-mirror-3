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
    *SecureTicketService* is used to create and validate *SecureTickets*.
    *SecureTickets* are light-weight symmetrically signed data sets with
    a limited lifestpan.

    The *key* passed to *SecureTicketService* is the password and the
    security relies heavily on its strength.  It really should be a 32 byte
    random string as you gain integrity AND performance by using a key of
    32 bytes length (it's padded or replaced by SHA256-hashes of itself
    to make it 32 bytes anyways).
    For your convenience, classmethod *create_random_key()* is provided:

    >>> key = SecureTicketService.create_random_key()
    >>> assert len(key) == 32
    >>> sts = SecureTicketService(key)

    A SecureTicket *ticket* which is successfully validated using
    ``SecureTicketService.validate_ticket()`` can only be created by
    someone who has knowledge of *key*. The entire contents of *ticket* is
    securely hashed using *key* and any change to *ticket* breaks the hash
    validation.

    >>> key = 'Io5IpK9ZTsKpG1ybaLCHkOH4kvHaTEO2imHvkqLVn7I='
    >>> sts = SecureTicketService(key.decode('base64'))
    >>> ticket = sts.create_ticket('someData')
    >>> ticket.data
    'someData'
    >>> sts.validate_ticket(ticket)
    True
    >>> sts2 = SecureTicketService('someOtherKey')
    >>> sts2.validate_ticket(ticket)
    False

    **entropy**

    The optional second argument *entropy* to *create_ticket()*, which must be
    a string if supplied, cannot be obtained from a ticket; it's just
    concatinated together with the rest of ticket when the hash is created.
    The same *entropy* value must therefore be used in
    ``SecureTicketService.validate_hash()`` or else validation fails.

    >>> ticket = sts.create_ticket('someKey', 'someEntropy')
    >>> sts.validate_ticket(ticket)
    False
    >>> sts.validate_ticket(ticket, 'someEntropy')
    True

    **session**

    Many use cases for secure tickets involves (or should involve) the concept
    of a session to prevent various types of attacks. The optional second
    argument *session* to *SecureTicketService()* is used in the same manner as
    *entropy*, but is supplied during *SecureTicketService* instantiation
    instead of during ticket creation.

    >>> sts = SecureTicketService(key, 'someSessionIdentifier')
    
    **options**

    Encryption, serialization and compression of *ticket*'s contents is
    optional. Encrypted tickets will have all its data and metadata encrypted
    with the *key* supplied to *SecureTicketService*. Serialization allows
    complex data types in *data* instead of just strings.  Compression
    (zlib) is useful if the *data* argument is inconveniently large.
    Options and their default values:

        * serialize=False
        * encrypt=False
        * compress=False

    Encrypted ticket attributes must be viewed through a *SecureTicketService*
    instance which provide transparent decryption:

    >>> key = SecureTicketService.create_random_key()
    >>> sts = SecureTicketService(key, serialize=1, compress=1, encrypt=1)
    >>> ticket = sts.create_ticket(['asd', 123], 'ee')
    >>> assert sts.get_data(ticket) == sts(ticket).data == ['asd', 123]
'''

__version__ = '0.9.2'

__all__ = []

from tickets.core import SecureTicketException
from tickets.core import SecureTicketValidationException
from tickets.core import InvalidTicketException
from tickets.core import SecureTicketPublicFlags
from tickets.core import SecureTicketFlags
from tickets.core import SecureTicket
from tickets.core import SecureTicketService

__all__ += [
    'SecureTicketException',
    'SecureTicketValidationException',
    'InvalidTicketException',
    'SecureTicketPublicFlags',
    'SecureTicketFlags',
    'SecureTicket',
    'SecureTicketService',
]

from tickets.web.forms import FormTicketService

__all__ += [
    'FormTicketService',
]



def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
