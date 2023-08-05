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

"""Unit tests for the passwords module."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    ]


import unittest

# Python 3 does not have the izip form.
try:
    from itertools import izip_longest as longest
except ImportError:
    from itertools import zip_longest as longest

from flufl.password._hash import make_secret
from flufl.password._registry import BadPasswordSchemeError, lookup
from flufl.password._verify import verify
from flufl.password import schemes, generate



class PasswordsTestBase:
    scheme = None

    def setUp(self):
        # The user's password, as a bytes
        self.pwbyte     = b'abc'
        self.pwutf8     = 'abc\xc3\xbf'             # 'abc\xff'
        # Bad passwords; bytes
        self.badbyte    = b'def'

    def test_byte_passwords(self):
        secret = make_secret(self.pwbyte, self.scheme)
        self.assertTrue(verify(secret, self.pwbyte), self.scheme)
        self.assertFalse(verify(secret, self.badbyte), self.scheme)

    def test_utf8_passwords(self):
        secret = make_secret(self.pwutf8, self.scheme)
        self.assertTrue(verify(secret, self.pwutf8), self.scheme)
        self.assertFalse(verify(secret, self.badbyte), self.scheme)



class TestNoPasswords(unittest.TestCase):
    def test_make_secret(self):
        self.assertEqual(schemes.NoPasswordScheme.make_secret('whatever'), b'')

    def test_check_response(self):
        self.assertFalse(
            schemes.NoPasswordScheme.check_response(b'foo', 'bar'))
        self.assertFalse(schemes.NoPasswordScheme.check_response(b'', 'bar'))



class TestCleartextPasswords(PasswordsTestBase, unittest.TestCase):
    scheme = schemes.ClearTextPasswordScheme


class TestSHAPasswords(PasswordsTestBase, unittest.TestCase):
    scheme = schemes.SHAPasswordScheme


class TestSSHAPasswords(PasswordsTestBase, unittest.TestCase):
    scheme = schemes.SSHAPasswordScheme


class TestPBKDF2Passwords(PasswordsTestBase, unittest.TestCase):
    scheme = schemes.PBKDF2PasswordScheme



class TestSchemeLookup(unittest.TestCase):
    def test_scheme_name_lookup(self):
        self.assertEqual(lookup('NONE'), schemes.NoPasswordScheme)
        self.assertEqual(lookup('CLEARTEXT'), schemes.ClearTextPasswordScheme)
        self.assertEqual(lookup('SHA'), schemes.SHAPasswordScheme)
        self.assertEqual(lookup('SSHA'), schemes.SSHAPasswordScheme)
        self.assertEqual(lookup('PBKDF2'), schemes.PBKDF2PasswordScheme)

    def test_lookup_error(self):
        self.assertRaises(BadPasswordSchemeError, lookup, 'BOGUS')




# See itertools doc page examples.
def _grouper(seq):
    args = [iter(seq)] * 2
    return list(longest(*args))


class TestPasswordGeneration(unittest.TestCase):
    def test_provided_user_friendly_password_length(self):
        self.assertEqual(len(generate(12)), 12)

    def test_provided_odd_user_friendly_password_length(self):
        self.assertEqual(len(generate(15)), 15)

    def test_user_friendly_password(self):
        password = generate()
        for pair in _grouper(password):
            # There will always be one vowel and one non-vowel.
            vowel = (pair[0] if pair[0] in 'aeiou' else pair[1])
            consonant = (pair[0] if pair[0] not in 'aeiou' else pair[1])
            self.assertTrue(vowel in 'aeiou', vowel)
            self.assertTrue(consonant not in 'aeiou', consonant)
