#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors:
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
    #'SecureTicketException',
    #'SecureTicketValidationException',
    #'InvalidTicketException',
    #'SecureTicketPublicFlags',
    #'SecureTicketFlags',
    #'SecureTicket',
    #'SecureTicketService',
]

import struct
import hmac
import hashlib
import uuid
import zlib
import base64
import time
import datetime
import pdb
import pickle
import cPickle

from tickets.bytemapper import ByteMapperFactory
import tickets.crypto
import tickets.flags

#
# Warn if SecureTicket's ticket.valid_until is accessed while being zero, as this usually
# indicates that valid_until is encrypted and needs to be obtained through
# SecureTicketService.get_valid_until(ticket) instead.
#
WARN_EMPTY_VALID_UNTIL = 0



class SecureTicketException(Exception): pass

class SecureTicketValidationException(SecureTicketException): pass
class InvalidTicketException(SecureTicketValidationException): pass




SecureTicketPublicFlags = tickets.flags.FlagsFactory(
    'SecureTicketPublicFlags',
    8,
    [
        ('encrypt', False),
    ]
)

SecureTicketFlags = tickets.flags.FlagsFactory(
    'SecureTicketFlags',
    8,
    [
        #
        # These flags in a ticket informs getter methods wether or not
        # data is serialized and/or compressed.
        #
        ('serialize',         False),
        ('compress',          False),
    ]
)

_SecureTicket = ByteMapperFactory(
    '_SecureTicket',
    [
        (4,  'prefix'),
        (20, 'hash'),
        (16, 'salt'),
        (4,  'ticket_len'),
        (1,  'public_flags'),
        (1,  'flags'),
        (4,  'valid_until'),
        (4,  'data_len'),
    ]
)





class SecureTicket(_SecureTicket):
    '''
    Instances of *SecureTicket* should generally be obtained through
    ``SecureTicketService.create_ticket()``, alternatively through calls to
    the classmethods ``SecureTicket.fromstring()`` or
    ``SecureTicket.frombase64()``.
    '''

    VISIBLE_MESSAGE_OFFSET = _SecureTicket.SALT_OFFSET
    CIPHERTEXT_OFFSET      = _SecureTicket.FLAGS_OFFSET
    DATA_OFFSET            = _SecureTicket.DATA_LEN_OFFSET +\
                                _SecureTicket.DATA_LEN_LEN

    MAX_LEN             = 2**32-1 # too large actualy, ticket uses some bytes
    VISIBLE_MESSAGE_LEN = MAX_LEN
    DATA_LEN            = MAX_LEN

    HASH_TYPE = 'sha256'

    SECURE_TICKET_PREFIX = struct.pack('I', 0x5ec71c37) # "secticet"

    _pickler = cPickle
    #_pickler = pickle

    def __init__(self, **kw):
        self._kw = kw

    @classmethod
    def _create_plaintext(cls, flags, valid_until, data, **kw):
        kw = flags.d
        flags       = cls._serialize_flags(flags, **kw)
        valid_until = cls._serialize_valid_until(valid_until, **kw)
        data        = cls._serialize_data(data, **kw)
        data_len    = cls._serialize_data_len(len(data), **kw)
        return cls._join_strings(dict(
                    flags       = flags,
                    valid_until = valid_until,
                    data_len    = data_len,
                    data        = data
        ))

    @classmethod
    def _create_messages(cls, salt, public_flags, flags,
                         valid_until, data, entropy, **kw):
        visible_message = ''
        ticket_len = None
        if public_flags.encrypt:
            ciphertext = kw['ciphertext']
            salt = cls._serialize_salt(salt, **kw)
            public_flags = cls._serialize_public_flags(public_flags, **kw)

            # length of ticket_len not added ??? 
            ticket_len = len(cls.SECURE_TICKET_PREFIX) +\
                         cls.HASH_LEN                  +\
                         len(salt +  public_flags + ciphertext)
            ticket_len += len(cls._serialize_ticket_len(0))
            ticket_len = cls._serialize_ticket_len(ticket_len, **kw)

            visible_message = cls._join_strings(dict(
                salt         = salt,
                ticket_len   = ticket_len,
                public_flags = public_flags,
                data         = ciphertext
            ))
        else:
            salt         = cls._serialize_salt(salt, **kw)
            public_flags = cls._serialize_public_flags(public_flags, **kw)
            flags        = cls._serialize_flags(flags, **kw)
            valid_until  = cls._serialize_valid_until(valid_until, **kw)
            data         = cls._serialize_data(data, **kw)
            data_len     = cls._serialize_data_len(len(data), **kw)

            ticket_len = len(cls.SECURE_TICKET_PREFIX) +\
                         cls.HASH_LEN                  +\
                         len(salt + public_flags + flags +\
                             valid_until + data_len + data)
            ticket_len += len(cls._serialize_ticket_len(0, **kw))
            ticket_len = cls._serialize_ticket_len(ticket_len, **kw)

            visible_message = cls._join_strings(dict(
                salt         = salt,
                ticket_len   = ticket_len,
                public_flags = public_flags,
                flags        = flags,
                valid_until  = valid_until,
                data_len     = data_len,
                data         = data
            ))
        entropy = cls._serialize_entropy(entropy)
        message = visible_message + salt + entropy
        return (message, visible_message)

    @classmethod
    def _create_message(cls, salt, public_flags, flags, valid_until, data, entropy, **kw):
        t = cls._create_messages(
            salt, public_flags, flags, valid_until, data, entropy, **kw
        )
        return t[0]

    @classmethod
    def _create_visible_message(cls, salt, public_flags, flags, valid_until, data, entropy, **kw):
        t = cls._create_messages(
            salt, public_flags, flags, valid_until, data, entropy, **kw
        )
        return t[1]

    def _load(self, hash_, visible_message):
        self._bytes = self.SECURE_TICKET_PREFIX + hash_ + visible_message
        return self

    def _load_from_parts(self, hash_, salt, public_flags,
             flags, valid_until, data, **kw):
        '''
            Loading a *SecureTicket* assumes a hash to exist.
        '''
        visible_message = self._create_visible_message(
            salt, public_flags, flags, valid_until, data, '', **kw)
        self._load(hash_, visible_message)
        return self

    def _set_bytes(self, bytes):
        self._bytes = bytes

    @classmethod
    def _split_deserialize_ticket_plaintext_strings(cls, joined_strings, names):
        '''
            special version of ByteMapper's _split_deserialize_strings() which
            supplies the flags dictionary, also contained within the
            serialized strings, in deserialization of the other values.
            Also, data_len is put in kwargs passed to deserialize() functions,
            since 'data' is null-padded if encrypted and needs a chomp.
        '''
        def string_start_offset(name):
            return getattr(cls, name.upper()+'_OFFSET')
        #
        # first loop joined_strings to find flags and data_len
        #
        flags = None
        data_len = None
        _joined_strings = joined_strings
        for name in sorted(names, key=string_start_offset):
            len_ = getattr(cls, name.upper()+'_LEN')
            string = _joined_strings[:len_]
            _joined_strings = _joined_strings[len_:]
            if name == 'flags':
                deserialize = getattr(cls, '_deserialize_'+name)
                flags = deserialize(string)
            if name == 'data_len':
                deserialize = getattr(cls, '_deserialize_'+name)
                data_len = deserialize(string)
            if not (flags is None) and not (data_len is None):
                break
        assert not flags is None
        assert not data_len is None
        kw = flags.d
        kw['data_len'] = data_len
        #
        # loop again and deserialize everything using flags and data_len
        #
        sorted_values = []
        _joined_strings = joined_strings
        for name in sorted(names, key=string_start_offset):
            len_ = getattr(cls, name.upper()+'_LEN')
            string = _joined_strings[:len_]
            #
            # encrypted data is null-padded to 16-byte alignment
            #
            #if name == 'data':
            #    string = string[:data_len] 
            #if name == 'data':
            #    print 'DATA:%d'%data_len, repr(string)
            _joined_strings = _joined_strings[len_:]
            deserialize = getattr(cls, '_deserialize_'+name)
            val = deserialize(string, **kw)
            sorted_values.append(val)
        return tuple(sorted_values)

    @classmethod
    def _split_deserialize_plaintext_into_tuple(cls, plaintext):
        parts = ('flags', 'valid_until', 'data_len', 'data')
        (flags, valid_until, data_len, data) = \
            cls._split_deserialize_ticket_plaintext_strings(plaintext, parts)
        #data = data[:data_len]
        return (flags, valid_until, data_len, data)

    @classmethod
    def _split_deserialize_plaintext_into_dict(cls, plaintext):
        (flags, valid_until, data_len, data) = \
            cls._split_deserialize_plaintext_into_tuple(plaintext)
        return dict(flags=flags, valid_until=valid_until,
                    data_len=data_len, data=data)
        
    def _recreate_message(self, entropy):
        # _serialize_entropy() doesn't see flags if ticket is encrypted and
        # thus can't [de]serialize based on flags.
        return self.visible_message + self.salt + self._serialize_entropy(entropy)

    @classmethod
    def _parse_visible_message(cls, b):
        return b[cls.VISIBLE_MESSAGE_OFFSET:]

    @classmethod
    def _parse_ciphertext(cls, b):
        return b[cls.CIPHERTEXT_OFFSET:]

    @classmethod
    def _parse_data(cls, b):
        return b[cls.DATA_OFFSET:]


    ######## serialization ########

    #
    # ticket_len
    #
    @classmethod
    def _serialize_ticket_len(cls, val, **kw):
        return struct.pack('I', val)

    @classmethod
    def _deserialize_ticket_len(cls, val, **kw):
        return struct.unpack('I', val)[0]

    #
    # public_flags
    #
    @classmethod
    def _serialize_public_flags(cls, val, **kw):
        return val._serialize()

    @classmethod
    def _deserialize_public_flags(cls, val, **kw):
        return SecureTicketPublicFlags._deserialize(val)

    #
    # flags
    #
    @classmethod
    def _serialize_flags(cls, val, **kw):
        return val._serialize()

    @classmethod
    def _deserialize_flags(cls, val, **kw):
        return SecureTicketFlags._deserialize(val)

    #
    # valid_until
    #
    @classmethod
    def _serialize_valid_until(cls, val, **kw):
        return struct.pack('I', int(val))

    @classmethod
    def _deserialize_valid_until(cls, val, **kw):
        return struct.unpack('I', val)[0] 

    #
    # data_len
    #
    @classmethod
    def _serialize_data_len(cls, val, **kw):
        return struct.pack('I', int(val))

    @classmethod
    def _deserialize_data_len(cls, val, **kw):
        return struct.unpack('I', val)[0] 

    #
    # data
    #
    @classmethod
    def _serialize_data(cls, val, **kw):
        if kw.get('serialize'):
            val = cls._pickler.dumps(val)
        if kw.get('compress'):
            val = zlib.compress(val)
        return val

    @classmethod
    def _deserialize_data(cls, val, **kw):
        if 'data_len' in kw:
            data_len = kw['data_len']
            if len(val) != data_len:
                val = val[:data_len]
        if kw.get('compress'):
            val = zlib.decompress(val)
        if kw.get('serialize'):
            val = cls._pickler.loads(val)
        return val

    #
    # entropy
    #
    @classmethod
    def _serialize_entropy(cls, val):
        return val

    @classmethod
    def _deserialize_entropy(cls, val):
        return val

    #
    # getters for potentially encrypted attributes
    #
    def _get_public_flags(self):
        #
        # Public_flags should not be magically serialized based on flags
        # contents here, as flags is not available here in encrypted tickets.
        #
        return self.__class__._deserialize_public_flags(self.raw_public_flags)

    def _get_flags(self):
        if self.public_flags.encrypt:
            msg = 'flags is encrypted, use SecureTicketService(key)(ticket).flags'
            msg += ' or SecureTicketService(key).get_flags(ticket) instead.'
            raise SecureTicketException(msg)
        return self.__class__._deserialize_flags(self.raw_flags,
                                                 **self.flags.d)

    def _get_valid_until(self):
        if self.public_flags.encrypt:
            msg = 'valid_until is encrypted, use SecureTicketService(key)(ticket).valid_until'
            msg += ' or SecureTicketService(key).get_valid_until(ticket) instead.'
            raise SecureTicketException(msg)
        return self.__class__._deserialize_valid_until(self.raw_valid_until,
                                                       **self.flags.d)

    def _get_data_len(self):
        if self.public_flags.encrypt:
            msg = 'data_len is encrypted, use SecureTicketService(key)(ticket).data_len'
            msg += ' or SecureTicketService(key).get_data_len(ticket) instead.'
            raise SecureTicketException(msg)
        return self.__class__._deserialize_data_len(self.raw_data_len,
                                                    **self.flags.d)

    def _get_data(self):
        if self.public_flags.encrypt:
            msg = 'data is encrypted, use SecureTicketService(key)(ticket).data'
            msg += ' or SecureTicketService(key).get_data(ticket) instead.'
            raise SecureTicketException(msg)
        return self.__class__._deserialize_data(self.raw_data, 
                                                **self.flags.d)


    #
    # properties
    #
    bytes             = property(lambda self : self._bytes)
    visible_message   = property(lambda self : self.__class__._parse_visible_message(self._bytes))
    raw_public_flags  = property(lambda self : self.__class__._parse_public_flags(self._bytes))
    raw_flags         = property(lambda self : self.__class__._parse_flags(self._bytes))
    raw_valid_until   = property(lambda self : self.__class__._parse_valid_until(self._bytes))
    raw_data_len      = property(lambda self : self.__class__._parse_data_len(self._bytes))
    raw_data          = property(lambda self : self.__class__._parse_data(self._bytes))
    data              = property(_get_data)
    ciphertext        = property(lambda self : self.__class__._parse_ciphertext(self._bytes))

    is_encrypted      = property(lambda self : self.public_flags.encrypt)


    def _looks_like_ticket(self):
        return self.prefix == self.SECURE_TICKET_PREFIX

    #
    # public methods
    #
    def tostring(self):
        return self._bytes

    def tobase64(self):
        return base64.b64encode(self.tostring())

    @classmethod
    def fromstring(cls, b):
        ticket = cls()
        ticket._set_bytes(b)
        return ticket

    @classmethod
    def frombase64(cls, b):
        return cls.fromstring(base64.b64decode(b))






class SecureTicketService(object):
    '''
    Some examples:

    Create a random key (use outcommented code):

    >>> #key = SecureTicketService.create_random_key()
    >>> key = 'make doctests work by using static key'

    Lets serialize some data and store in a ticket:

    >>> sts = SecureTicketService(key, serialize=1)
    >>> ticket = sts.create_ticket(['asd', 123, True, None, ['yay']])
    >>> assert type(ticket.data) is list
    >>> assert ticket.data[0] == 'asd'
    >>> assert ticket.data[4][0] == 'yay'

    Lets store a huge text payload with and without compression. First we
    disable serialization which means that only string-type *data* is allowed.

    >>> sts.options.set_serialize(0)
    >>> data = 'A' * 10**5 # 100k
    >>> large = sts.create_ticket(data)
    >>> len(large.data)
    100000
    >>> len(large.tostring())
    100054
    >>> small = sts.create_ticket(data, compress=1)
    >>> len(small.data)
    100000
    >>> len(small.tostring())
    175
    >>> large.data[:5] == small.data[:5] == 'AAAAA'
    True

    What if we want to give a ticket containing secret information to a third
    party, without revealing the ticket contents? By default, the data field is
    in plaintext (albeit protected from manipulation thanks to hashing with our
    secret key). Concider the simple example below:

    >>> plaintext = 'my precious'
    >>> ticket = sts.create_ticket(plaintext)
    >>> ticket.tostring().find('my precious')
    54

    If we enable encryption, all information in ticket is encrypted, including
    metadata, except for the bit flag marking the ticket as encrypted and the
    ticket length field. Encryption algorithm is AES128-CBC from pyCrypto
    (which must be installed) and the key used is the *key* supplied during
    *SecureTicketService* instantiation.

    Data can still be transparently accessed using a *SecureTicketService*
    instance.

    >>> sts.options.set_encrypt(1)
    >>> ticket = sts.create_ticket(plaintext)
    >>> ticket.tostring().find('my precious')
    -1
    >>> sts(ticket).data
    'my precious'

    To enable all features upon *SecureTicketService* instantiation, simply
    use:

    >>> sts = SecureTicketService(key, serialize=1, encrypt=1, compress=1)
    '''

    DEFAULT_TICKET_LIFESPAN = 1200 # 1200 seconds, 20 minutes

    def __init__(self, key, session='', ticket_class=SecureTicket, **options):
        self.options         = self.SecureTicketServiceOptions(**options)
        self._key            = key
        self._session        = session
        self._ticket_class   = ticket_class
        self._flags          = SecureTicketFlags()
        self._public_flags   = SecureTicketPublicFlags()
        self.ticket_lifespan = self.DEFAULT_TICKET_LIFESPAN
        self._flags.sync(self.options)
        self._public_flags.sync(self.options)
        hashfunc           = getattr(hashlib, ticket_class.HASH_TYPE)
        self._hmac_factory = lambda : hmac.HMAC(key, msg='', digestmod=hashfunc)

    class SecureTicketProxy(object):
        def __init__(self, sts, ticket):
            self._sts = sts
            self._ticket = ticket
        hash          = property(lambda self : self._ticket.hash)
        salt          = property(lambda self : self._ticket.salt)
        ticket_len    = property(lambda self : self._ticket.ticket_len)
        public_flags  = property(lambda self : self._ticket.public_flags)
        flags         = property(lambda self : self._sts.get_flags(self._ticket))
        valid_until   = property(lambda self : self._sts.get_valid_until(self._ticket))
        data_len      = property(lambda self : self._sts.get_data_len(self._ticket))
        data          = property(lambda self : self._sts.get_data(self._ticket))

    class SecureTicketHelper(object):
        pass

    class SecureTicketEncryptor(SecureTicketHelper):
        def __init__(self, encrypt_func):
            self._encrypt_func = encrypt_func
        def __call__(self, plaintext):
            return self._encrypt_func(plaintext)

    class SecureTicketHasher(SecureTicketHelper):
        def __init__(self, hash_func):
            self._hash_func = hash_func
        def __call__(self, message):
            return self._hash_func(message)

    SecureTicketServiceOptions = tickets.flags.FlagsFactory(
        'SecureTicketServiceOptions',
        32,
        [
            ('encrypt',           False),
            ('serialize',         False),
            ('compress',          False),
        ]
    )
    #SecureTicketServiceOptions._ignore_invalid_names_on_init = True

    @classmethod
    def _new_entropy(self, size):
        '''
            Do not use _new_entropy() to create entropy for *create_ticket()*.
            The _new_entropy() method returns random junk while *entropy* in
            *create_ticket()* is intended for information.
        '''
        entropy = ''
        while len(entropy) < size:
            entropy += uuid.uuid4().bytes
        return entropy[:size]

    @classmethod
    def create_random_key(cls):
        '''
            Create a key suitable for use in *SecureTicketSession*.
        '''
        return cls._new_entropy(32)

    @classmethod
    def create_random_session(cls):
        '''
            Create a session variable suitable for use in *SecureTicketSession*.
        '''
        return cls._new_entropy(32)


    def __call__(self, ticket):
        return self.SecureTicketProxy(self, ticket)

    def _new_salt(self):
        return self._new_entropy(self._ticket_class.SALT_LEN)

    def _new_hasher(self):
        hmac = self._hmac_factory()
        hash_len = self._ticket_class.HASH_LEN
        def hasher(message):
            hmac.update(message)
            return hmac.digest()[:hash_len]
        return self.SecureTicketHasher(hasher)

    def _hash_message(self, message):
        hasher = self._new_hasher()
        hash_ = hasher(message)
        assert len(hash_) == self._ticket_class.HASH_LEN
        return hash_

    def _encrypt(self, salt, plaintext):
        saes = tickets.crypto.AES(self._key)
        return saes.encrypt(salt, plaintext)

    def _decrypt_first_block(self, ticket):
        '''
            Like _decrypt_ticket_into_tuple() but faster as only one block is
            decrypted. The drawback is that at most 7 bytes of data is returned.

            returns (flags, valid_until, data_len, possibly_partial_data) 
        '''
        aes = tickets.crypto.AES(self._key)
        block = aes.decrypt_first_block(self.salt, ticket.ciphertext)
        (flags, valid_until, data_len, data) =\
            ticket.__class__._split_deserialize_plaintext_into_tuple(block)
        return (flags, valid_until, data_len, data)

    def _decrypt_plaintext_from_ticket(self, ticket):
        aes = tickets.crypto.AES(self._key)
        plaintext = aes.decrypt(ticket.salt, ticket.ciphertext)
        return plaintext

    def _decrypt_ticket_into_tuple(self, ticket):
        '''
            returns decrypted deserialized tuple with the following values:
            (flags, valid_until, data_len, data)
        '''
        plaintext = self._decrypt_plaintext_from_ticket(ticket)
        return ticket.__class__._split_deserialize_plaintext_into_tuple(plaintext)

    def _decrypt_ticket_into_dict(self, ticket):
        '''
            returns decrypted deserialized dict with the following keys:
            'flags', 'valid_until', 'data_len', 'data'
        '''
        plaintext = self._decrypt_plaintext_from_ticket(ticket)
        return ticket.__class__._split_deserialize_plaintext_into_dict(plaintext)


    #
    # decrypt specific parts
    #
    def _decrypt_flags(self, ticket):
        (flags, valid_until, data_len) = \
            self._decrypt_first_block(ticket)
        return flags

    def _decrypt_valid_until(self, ticket):
        (flags, valid_until, data_len) = \
            self._decrypt_first_block(ticket)
        return valid_until

    def _decrypt_data_len(self, ticket):
        (flags, valid_until, data_len) = \
            self._decrypt_first_block(ticket)
        return data_len

    def _decrypt_data(self, ticket):
        (flags, valid_until, data_len, data) = \
            self._decrypt_ticket_into_tuple(ticket)
        return data


    def _add_session_to_entropy(self, salt, entropy):
        #
        # avoid collisions by putting salt between session and entropy
        #
        if self._session:
            entropy = self._session + salt + entropy
        return entropy

    def _new_encryptor(self, iv):
        aes = tickets.crypto.AES(self._key)
        encrypt = lambda plaintext : aes.encrypt(iv, plaintext)
        return self.SecureTicketEncryptor(encrypt)

    def _new_valid_until(self):
        return int(time.time() + self.ticket_lifespan)

    def _create_ticket(self, ticket_class, salt, public_flags, flags,
                       valid_until, data, entropy):
        kw = flags.d
        entropy = self._add_session_to_entropy(salt, entropy)
        if public_flags.encrypt:
            plaintext = ticket_class._create_plaintext(
                flags, valid_until, data, **kw
            )
            flags = valid_until = data = None
            encrypt = self._new_encryptor(salt)
            ciphertext = encrypt(plaintext)
            kw['ciphertext'] = ciphertext
        #
        # Note that the contents of 'flags' are leaked to _create_messages
        # through kw, even if 'flags' is encrypted within ciphertext.
        #
        message, visible_message = ticket_class._create_messages(
            salt, public_flags, flags, valid_until, data, entropy, **kw
        )
        hash_ = self._hash_message(message)

        ticket = ticket_class()._load(hash_, visible_message)
        return ticket

    #
    # user interface
    #

    def set_default_public_flags(self, flags):
        self._public_flags = flags

    def set_default_flags(self, flags):
        self._flags = flags

    def create_ticket(self, data='', entropy='', **options):
        '''
            Create a *SecureTicket* containing *data*. If *entropy* is specified,
            the same *entropy* must be supplied when using *validate_ticket()*,
            or else validation will fail.

            Options can be used to override *SecureTicketService* default
            options.
        '''
        options = self.options.copy_update(**options)

        ticket_class = self._ticket_class
        salt         = self._new_salt()
        public_flags = self._public_flags.copy_sync(options)
        flags        = self._flags.copy_sync(options)
        valid_until  = self._new_valid_until()
        ticket = self._create_ticket(ticket_class, salt, public_flags, flags,
                                      valid_until, data, entropy)
        return ticket

    def validate_ticket(self, ticket, entropy=''):
        '''
            Validate the integrity of *ticket* by recreating its hash and
            verifying that it matches ``ticket.hash``. The validity of
            *ticket*'s lifespan is also verified.
            The 'entropy' argument must match what was used in the call to
            create_ticket().
        '''
        ticket_class = self._ticket_class
        #
        if not ticket._looks_like_ticket():
            msg = 'Ticket broken, invalid prefix: {0}'
            msg = msg.format(repr(ticket.prefix))
            raise InvalidTicketException(msg)
        if not ticket.ticket_len == len(ticket._bytes):
            msg = 'Ticket broken, ticket.ticket_len({0}) != {1}'
            msg = msg.format(ticket.ticket_len, len(ticket._bytes))
            raise InvalidTicketException(msg)
        now = time.time()
        if entropy is None:
            entropy = ''
        entropy = self._add_session_to_entropy(ticket.salt, entropy)
        message = ticket._recreate_message(entropy)
        if self._hash_message(message) != ticket.hash:
            return False
        if self(ticket).valid_until < now:
            return False
        return True


    #
    # ticket attributes; transparent decryption
    #
    def get_flags(self, ticket):
        '''
            Get ``ticket.flags`` and transparently decrypt if necessary.
            Synonymous to ``sts(ticket).flags``, with *sts* being the *SecureTicketService*.
        '''
        flags = None
        if ticket.public_flags.encrypt:
            flags = self._decrypt_ticket_into_tuple(ticket)[0]
        else:
            flags = ticket.flags
        return flags

    def get_valid_until(self, ticket):
        '''
            Get ``ticket.valid_until`` and transparently decrypt if necessary.
            Synonymous to ``sts(ticket).valid_until``, with *sts* being the *SecureTicketService*.
        '''
        valid_until = None
        if ticket.public_flags.encrypt:
            valid_until = self._decrypt_ticket_into_tuple(ticket)[1]
        else:
            valid_until = ticket.valid_until
        return valid_until

    def get_data_len(self, ticket):
        '''
            Get ``ticket.data_len`` and transparently decrypt if necessary.
            Synonymous to ``sts(ticket).data_len``, with *sts* being the *SecureTicketService*.
        '''
        data_len = None
        if ticket.public_flags.encrypt:
            data_len = self._decrypt_ticket_into_tuple(ticket)[2]
        else:
            data_len = ticket.data_len
        return data_len

    def get_data(self, ticket):
        '''
            Get ``ticket.data`` and transparently decrypt and gunzip if necessary.
            Synonymous to ``sts(ticket).data``, with *sts* being the *SecureTicketService*.
        '''
        data = None
        if ticket.public_flags.encrypt:
            data = self._decrypt_ticket_into_tuple(ticket)[3]
        else:
            data = ticket.data
        return data






def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()

