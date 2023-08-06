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

"""User-friendly password generation."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'generate',
    ]


import random

from itertools import chain, product
from string import ascii_lowercase


EMPTYSTRING = ''



_vowels = tuple('aeiou')
_consonants = tuple(c for c in ascii_lowercase if c not in _vowels)
_syllables = tuple(x + y for (x, y) in
                   chain(product(_vowels, _consonants),
                         product(_consonants, _vowels)))



def generate(length=8):
    """Make a random *user friendly* password.

    Such passwords are nominally easier to pronounce and thus remember.  Their
    security in relationship to purely random passwords has not been
    determined.

    :param length: Minimum length in characters for the resulting password.
        The password will always be an even number of characters.  The default
        is to create passwords of length 8.
    :type length: int
    :return: The user friendly password.
    :rtype: string
    """
    syllables = []
    while len(syllables) * 2 < length:
        syllables.append(random.choice(_syllables))
    return EMPTYSTRING.join(syllables)[:length]
