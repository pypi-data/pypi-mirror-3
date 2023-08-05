#!/usr/bin/env python
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
import os
from setuptools import setup

import tickets

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pytickets",
    version = tickets.__version__,
    author = "Krister Hedfors",
    author_email = "krister@tripleaes.com",
    description = ("pyTickets are light-weight symmetrically signed data"
                   " containers with optional encryption, serialization and"
                   " compression of their contents."
    ),
    license = "GPL",
    keywords = "ticket tickets encrypt secure sign signed ignature hash hashed",
    url = "http://pytickets.tripleaes.com/",
    packages=[
        'tickets',
        'tickets.web',
        'tickets.tests'
    ],
    long_description=tickets.__doc__,
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Security :: Cryptography",
    ],
)

