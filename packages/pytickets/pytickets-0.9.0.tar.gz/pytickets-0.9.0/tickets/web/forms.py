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
FormTicketService, FormTicket
=============================
*FormTicketService* provides simple form validation based on
*SecureTicketService*.

Create a form ticket:

>>> key = FormTicketService.create_random_key()
>>> session = 'CurrentUserWebSession'
>>> fts = FormTicketService(key, session)
>>> action = '/some/action'
>>> param_names = ['foo', 'bar']
>>> ticket = fts.create_ticket(action, param_names)
>>> input_params = {'foo':'123'}

Ticket validation is controlled with options. Options (and their
default values) include:
    * *require_form_action=True*
    * *require_param_names=True*
    * *require_param_values=True*
    * *allow_undeclared_param_names=False*

If True, *require_form_action* requires the *form_action* specified upon ticket creation
to match the *form_action* passed to *validate_form*.

If True, *require_param_names* requires all parameter names in both *param_names* and
*params* passed to *create_ticket()* to be available in the *params* argument
passed to *validate_form()*.

If True, *require_param_values* requires param name and value pairs passed in *params*
to *create_ticket()* to exist in *params* passed to *validate_ticket()*.

If True, *allow_undeclared_param_names* allows other param names than what was
specified in *param_names* and *params* in call to *create_ticket()* to be passed to
*validate_form()*.

If any of these validations fail, one of the following exceptions will be
raised, containing a dict which exactly specifies what was passed and which params were
invalid:
    * *InvalidFormActionError*
    * *MissingParamNamesError*
    * *InvalidParamValuesError*
    * *UndeclaredParamNamesError*

'''


__all__ = [
    'FormTicketFlags',
    'FormTicket',
    'FormTicketService',

    'FormTicketValidationError',
    'InvalidFormActionError',
    'MissingParamNamesError',
    'InvalidParamValuesError',
    'UndeclaredParamNamesError',
]




import unittest
import doctest

import tickets
from tickets import SecureTicketValidationException
from tickets import SecureTicket
from tickets import SecureTicketService

import operator
import base64
#import pickle
import cPickle



FormTicketFlags =\
        tickets.flags.FormTicketFlags =\
        tickets.flags.FlagsFactory(
    'FormTicketFlags',
    8,
    [
        ("require_form_action",          True),
        ("require_param_names",          True),
        ("require_param_values",         True),
        ("allow_undeclared_param_names", False),
    ]
)


class FormTicketValidationException(SecureTicketValidationException): pass
class FormTicketValidationError(FormTicketValidationException): pass

class InvalidFormActionError(FormTicketValidationError): pass
class MissingParamNamesError(FormTicketValidationError): pass
class InvalidParamValuesError(FormTicketValidationError): pass
class UndeclaredParamNamesError(FormTicketValidationError): pass



class FormTicket(SecureTicket):
    def __str__(self):
        s = "FormTicket('" + self.tostring() + "')"
        return s
    ftflags              = property(lambda self : self.data[0])
    required_form_action = property(lambda self : self.data[1])
    required_param_names = property(lambda self : self.data[2])
    required_params      = property(lambda self : self.data[3])



class _FormTicketValidators(SecureTicketService):

    def _validate_required_form_action(self, ticket, action_to_validate):
        if ticket.required_form_action != action_to_validate:
            msg = 'Invalid form action: {0}'
            msg = msg.format(action_to_validate)
            err = dict( message=msg,
                        received=action_to_validate,
                        expected=ticket.required_form_action)
            raise InvalidFormActionError(err)
        return True

    def _validate_required_param_names(self, ticket, params_to_validate):
        missing_names = []
        for name in ticket.required_param_names:
            if not name in params_to_validate:
                missing_names.append(name)
        if missing_names:
            msg = 'Missing param names: {0}'
            msg = msg.format(', '.join(missing_names))
            err = dict( message=msg,
                        received=params_to_validate.keys(),
                        expected=ticket.required_param_names,
                        missing=tuple(missing_names))
            raise MissingParamNamesError(err)
        return True

    def _validate_required_param_values(self, ticket, params_to_validate):
        missing_names = []
        invalid_params = {}
        for (name, value) in ticket.required_params:
            if not name in params_to_validate:
                missing_names.append(name)
            if params_to_validate[name] != value:
                invalid_params[name] = params_to_validate[name]
        if missing_names:
            msg = 'Missing param names: {0}'
            msg = msg.format(', '.join(missing_names))
            err = dict( message=msg,
                        received=params_to_validate.keys(),
                        expected=dict(ticket.required_params).keys(),
                        missing=tuple(missing_names))
            raise MissingParamNamesError(err)
        if invalid_params:
            msg = 'Invalid param values: {0}'
            msg = msg.format(repr(invalid_params))
            err = dict( message=msg,
                        received=invalid_params,
                        expected=dict(ticket.required_params),
                        invalid=invalid_params)
            raise InvalidParamValuesError(err)
        return True

    def _validate_declared_param_names(self, ticket, params_to_validate):
        if len(params_to_validate) > len(ticket.required_param_names):
            names_to_validate    = params_to_validate.keys()
            required_param_names = ticket.required_param_names
            undeclared_names = set(names_to_validate) - set(required_param_names)
            undeclared_names = tuple(undeclared_names)
            msg = 'Undeclared param names received: {0}'
            msg = msg.format(tuple(undeclared_names))
            err = dict( message=msg,
                        received=undeclared_names,
                        expected=dict(ticket.required_params),
                        undeclared=undeclared_names)
            raise UndeclaredParamNamesError(err)
        return True



class FormTicketService(_FormTicketValidators):

    def __init__(self, key, session):
        options = dict(
            encrypt   = False,
            serialize = True,
            compress  = False,
        )
        SecureTicketService.__init__(
            self, key, session, ticket_class=FormTicket, **options
        )
        self.ftflags = FormTicketFlags()

    #
    # private
    #
    def _create_data(self, ftflags, form_action, param_names, indexed_param_values):
        return (ftflags, form_action, param_names, indexed_param_values)

    def create_ticket(self,
                      form_action='',
                      param_names=[],
                      params=[],
                      **options):
        '''
            fixme
        '''
        ftflags = self.ftflags.copy_update(**options)
        #
        if type(params) is dict:
            params = sorted(params.items())
        param_names = set(param_names)
        param_names |= set([t[0] for t in params])
        param_names = tuple(sorted(param_names))
        data = self._create_data(ftflags, form_action, param_names, params)
        entropy = ''
        return SecureTicketService.create_ticket(self, data, entropy)


    def validate_form(self, ticket, action_to_validate, params_to_validate):
        if type(params_to_validate) is list:
            params_to_validate = dict(params_to_validate)

        entropy = ''
        if not SecureTicketService.validate_ticket(self, ticket, entropy):
            return False
        ftflags = ticket.ftflags
        if ftflags.require_form_action:
            self._validate_required_form_action(ticket, action_to_validate)

        if ftflags.require_param_names:
            self._validate_required_param_names(ticket, params_to_validate)

        if not ftflags.allow_undeclared_param_names:
            self._validate_declared_param_names(ticket, params_to_validate)
            
        if ftflags.require_param_values:
            self._validate_required_param_values(ticket, params_to_validate)
        #print 'success'
        return True





class Test_FormTicketService(unittest.TestCase):
    def _test_test(self):
        assert 1==2

    def test_all_validators(self):
        session = 'JSESSASDQWE'
        fts = FormTicketService('some key', session)

        action = '/some/action'
        names  = ('aa', 'bb', 'foo')
        params = dict(aa='AA', bb='BB')

        params_good     = dict(aa='AA', bb='BB', foo='FOO')
        params_badval   = dict(aa='AA', bb='XX', foo='FOO')
        params_missing  = dict(aa='AA', bb='BB')
        params_extra    = dict(aa='AA', bb='BB', foo='FOO', bar='BAR')
        action_bad      = '/evil/action'

        #
        # default: strictest validation
        #
        ticket = fts.create_ticket(action, names, params)
        assert       fts.validate_form(ticket, action, params_good)
        self.assertRaises( InvalidFormActionError,
            lambda : fts.validate_form(ticket, action_bad, params_good))
        self.assertRaises( InvalidParamValuesError,
            lambda : fts.validate_form(ticket, action, params_badval))
        self.assertRaises( MissingParamNamesError,
            lambda : fts.validate_form(ticket, action, params_missing))
        self.assertRaises( UndeclaredParamNamesError,
            lambda : fts.validate_form(ticket, action, params_extra))

        #
        # require_form_action=False
        #
        ticket = fts.create_ticket(action, names, params,
            require_form_action=False)

        assert       fts.validate_form(ticket, action, params_good)
        assert       fts.validate_form(ticket, action_bad, params_good)
        self.assertRaises( InvalidParamValuesError,
            lambda : fts.validate_form(ticket, action, params_badval))
        self.assertRaises( MissingParamNamesError,
            lambda : fts.validate_form(ticket, action, params_missing))
        self.assertRaises( UndeclaredParamNamesError,
            lambda : fts.validate_form(ticket, action, params_extra))

        #
        # require_param_names=False
        #
        ticket = fts.create_ticket(action, names, params,
            require_param_names=False)

        assert       fts.validate_form(ticket, action, params_good)
        self.assertRaises( InvalidFormActionError,
            lambda : fts.validate_form(ticket, action_bad, params_good))
        self.assertRaises( InvalidParamValuesError,
            lambda : fts.validate_form(ticket, action, params_badval))
        assert       fts.validate_form(ticket, action, params_missing)
        self.assertRaises( UndeclaredParamNamesError,
            lambda : fts.validate_form(ticket, action, params_extra))

        #
        # require_param_values=False
        #
        ticket = fts.create_ticket(action, names, params,
            require_param_values=False)

        assert     fts.validate_form(ticket, action, params_good)
        self.assertRaises( InvalidFormActionError,
            lambda : fts.validate_form(ticket, action_bad, params_good))
        assert       fts.validate_form(ticket, action, params_badval)
        self.assertRaises( MissingParamNamesError,
            lambda : fts.validate_form(ticket, action, params_missing))
        self.assertRaises( UndeclaredParamNamesError,
            lambda : fts.validate_form(ticket, action, params_extra))

        #
        # allow_undeclared_param_names=True
        #
        ticket = fts.create_ticket(action, names, params,
            allow_undeclared_param_names=True)

        assert       fts.validate_form(ticket, action, params_good)
        self.assertRaises( InvalidFormActionError,
            lambda : fts.validate_form(ticket, action_bad, params_good))
        self.assertRaises( InvalidParamValuesError,
            lambda : fts.validate_form(ticket, action, params_badval))
        self.assertRaises( MissingParamNamesError,
            lambda : fts.validate_form(ticket, action, params_missing))
        assert       fts.validate_form(ticket, action, params_extra)




def _test():
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()

