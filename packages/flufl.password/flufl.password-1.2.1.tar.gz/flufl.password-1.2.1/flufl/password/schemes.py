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

"""Password hashing and verification schemes.

Represents passwords using RFC 2307 syntax (as best we can tell).
"""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'ClearTextPasswordScheme',
    'NoPasswordScheme',
    'PBKDF2PasswordScheme',
    'PasswordScheme',
    'SHAPasswordScheme',
    'SSHAPasswordScheme',
    ]


import os
import hmac
import hashlib

from array import array
from base64 import urlsafe_b64decode as decode
from base64 import urlsafe_b64encode as encode
from functools import partial

from flufl.password._registry import register
from flufl.password._utils import BadPasswordFormatError


SALT_LENGTH = 20 # bytes
ITERATIONS  = 2000



class PasswordScheme:
    """Password scheme base class."""
    TAG = ''

    @staticmethod
    def make_secret(password):
        """Return the hashed password.

        :param password: The clear text password.
        :type password: bytes or utf-8 encoded string.
        :return: The encrypted password.
        :rtype: bytes
        """
        raise NotImplementedError

    @classmethod
    def check_response(cls, hashed, cleartext, scheme=None):
        """Check a hashed password against a clear text response.

        :param hashed: The user's stored hashed password, without the scheme
            prefix (i.e. strip off the *{SCHEME}* part first).
        :type hashed: bytes
        :param cleartext: The clear text password entered by the user for
            authentication.
        :type cleartext: bytes or utf-8 encoded string.
        :param scheme: The scheme tag i.e. the *{SCHEME}* part without the
            braces.  This can be omitted when called on the class directly,
            unless the scheme puts some additional information in there.  It
            is always provided by the `verify()` API.
        :type response: bytes or utf-8 encoded string.
        :return: True if the clear text matches the hash
        :rtype: bool
        """
        return hashed == cls.make_secret(cleartext)



@register
class NoPasswordScheme(PasswordScheme):
    """A password scheme without passwords."""

    TAG = 'NONE'

    @staticmethod
    def make_secret(password):
        """See `PasswordScheme`."""
        return b''

    @classmethod
    def check_response(cls, hashed, cleartext, scheme=None):
        """See `PasswordScheme`."""
        return False



@register
class ClearTextPasswordScheme(PasswordScheme):
    """A password scheme that stores clear text passwords."""

    TAG = 'CLEARTEXT'

    @staticmethod
    def make_secret(password):
        """See `PasswordScheme`."""
        return password



@register
class SHAPasswordScheme(PasswordScheme):
    """A password scheme that encodes the password using SHA1."""

    TAG = 'SHA'

    @staticmethod
    def make_secret(password):
        """See `PasswordScheme`."""
        h = hashlib.sha1(password)
        return encode(h.digest())



@register
class SSHAPasswordScheme(PasswordScheme):
    """A password scheme that encodes the password using salted SHA1."""

    TAG = 'SSHA'

    @staticmethod
    def _make_salted_hash(password, salt):
        h = hashlib.sha1(password)
        h.update(salt)
        return encode(h.digest() + salt)

    @staticmethod
    def make_secret(password):
        """See `PasswordScheme`."""
        salt = os.urandom(SALT_LENGTH)
        return SSHAPasswordScheme._make_salted_hash(password, salt)

    @classmethod
    def check_response(cls, hashed, cleartext, scheme=None):
        """See `PasswordScheme`."""
        # The salt is always 20 bytes and always tacked onto the end.
        decoded = decode(hashed)
        salt = decoded[20:]
        return hashed == cls._make_salted_hash(cleartext, salt)



def _bytes_of(array_obj):
    # Avoid DeprecationWarnings in Python 3.
    try:
        return array_obj.tobytes()
    except AttributeError:
        return array_obj.tostring()


# Basic algorithm given by Bob Fleck
@register
class PBKDF2PasswordScheme(PasswordScheme):
    """RFC 2989 password encoding scheme."""

    # This is a bit nasty if we wanted a different prf or iterations.  OTOH,
    # we really have no clue what the standard LDAP-ish specification for
    # those options is.
    TAG = 'PBKDF2 SHA {0}'.format(ITERATIONS)

    @staticmethod
    def _pbkdf2(password, salt, iterations):
        """From RFC2898 sec. 5.2.  Simplified to handle only 20 byte output
        case.  Output of 20 bytes means always exactly one block to handle,
        and a constant block counter appended to the salt in the initial hmac
        update.
        """
        # We do it this way because the array() constructor takes a 'native
        # string'.  You can't use unicodes in Python 2 or bytes in Python 3.
        array_of_signedints = partial(array, str('i'))
        h = hmac.new(password, None, hashlib.sha1)
        prf = h.copy()
        prf.update(salt + b'\x00\x00\x00\x01')
        T = U = array_of_signedints(prf.digest())
        while iterations:
            prf = h.copy()
            prf.update(_bytes_of(U))
            U = array_of_signedints(prf.digest())
            T = array_of_signedints((t ^ u for t, u in zip(T, U)))
            iterations -= 1
        return _bytes_of(T)

    @staticmethod
    def make_secret(password):
        """See `PasswordScheme`.

        From RFC2898 sec. 5.2.  Simplified to handle only 20 byte output
        case.  Output of 20 bytes means always exactly one block to handle,
        and a constant block counter appended to the salt in the initial hmac
        update.
        """
        salt = os.urandom(SALT_LENGTH)
        digest = PBKDF2PasswordScheme._pbkdf2(password, salt, ITERATIONS)
        return encode(digest + salt)

    @classmethod
    def check_response(cls, hashed, cleartext, scheme):
        """See `PasswordScheme`."""
        parts = scheme.split()
        if (len(parts) != 3 or
            parts[0].upper() != 'PBKDF2' or
            parts[1].upper() != 'SHA'
            ):
            raise BadPasswordFormatError(scheme)
        try:
            iterations = int(parts[2])
        except ValueError:
            raise BadPasswordFormatError(scheme)
        decoded = decode(hashed)
        salt = decoded[20:]
        secret = decoded[:20]
        return secret == cls._pbkdf2(cleartext, salt, iterations)
