# Copyright (C) 2011-2012 by Barry A. Warsaw
#
# This file is part of flufl.password
#
# flufl.password is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# flufl.password is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.password.  If not, see <http://www.gnu.org/licenses/>.

"""Various utilities."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'BadPasswordFormatError',
    'split',
    ]


import re

SCHEME_RE = r'{(?P<scheme>[^}]+?)}(?P<rest>.*)'.encode()



class BadPasswordFormatError(Exception):
    """A badly formatted password hash was given."""



def split(hashed):
    mo = re.match(SCHEME_RE, hashed, re.IGNORECASE)
    if not mo:
        raise BadPasswordFormatError
    scheme, secret = mo.groups(('scheme', 'rest'))
    return scheme.decode('utf-8'), secret
