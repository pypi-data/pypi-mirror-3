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

"""Make secrets."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'make_secret',
    ]



def make_secret(password, scheme=None):
    """Return a hashed password using the given scheme.

    :param password: The plain text password to hash.
    :type password: bytes or utf-8 encoded string.
    :param scheme: The scheme class to use for encryption.  If not given, 
        `SSHAPasswordScheme` is used.
    :type scheme: PasswordScheme subclass.
    :return: The hashed password.
    :rtype: bytes
    """
    if not isinstance(password, bytes):
        # If it's not a bytes, it better be a unicode in Python 2 or a str in
        # Python 3.  Let encoding errors propagate up.
        password = password.encode('utf-8')
    if scheme is None:
        from flufl.password.schemes import SSHAPasswordScheme
        scheme = SSHAPasswordScheme
    secret = scheme.make_secret(password)
    if not isinstance(scheme.TAG, bytes):
        tag = scheme.TAG.encode('utf-8')
    return b'{' + tag + b'}' + secret
