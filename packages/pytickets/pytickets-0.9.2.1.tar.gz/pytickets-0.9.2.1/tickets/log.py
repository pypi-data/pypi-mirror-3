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
    'debug'
    'info'
    'warning'
    'error'
    'critical'
    'log'
]


import logging

FORMAT = '%(filename)s:%(lineno)d  %(message)s'

logging.basicConfig(
    format=FORMAT
)

debug    = logging.debug
info     = logging.info
warning  = logging.warning
error    = logging.error
critical = logging.critical
log      = logging.log


def _test():
    import doctest
    import unittest
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()

