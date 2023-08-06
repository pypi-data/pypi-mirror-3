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

"""Verification."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'verify',
    ]


from flufl.password._registry import lookup
from flufl.password._utils import split



def verify(hashed, cleartext):
    """Verify whether the clear text response matches the hashed challenge.

    :param hashed: The hashed password.
    :type hashed: bytes
    :param cleartext: The clear text password to match against.
    :type cleartext: bytes or utf-8 encoded string.
    :return: Flag indicating whether the password matched.
    :rtype: bool
    :raises BadPasswordSchemeError: when the indicated scheme cannot be found.
    :raises BadPasswordFormatError: when the hashed parameter is not properly
        formatted as ``{SCHEME}password``.
    """
    if not isinstance(cleartext, bytes):
        cleartext = cleartext.encode('utf-8')
    scheme, secret = split(hashed)
    scheme_class = lookup(scheme.upper())
    return scheme_class.check_response(secret, cleartext, scheme)
