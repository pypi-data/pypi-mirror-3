# Copyright (C) 2004-2012 by Barry A. Warsaw
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

"""Package init."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'BadPasswordFormatError',
    'BadPasswordSchemeError',
    '__version__',
    'generate',
    'lookup',
    'make_secret',
    'register',
    'verify',
    ]


__version__ = '1.2'


from ._hash import make_secret
from ._generate import generate
from ._registry import BadPasswordSchemeError, lookup, register
from ._utils import BadPasswordFormatError
from ._verify import verify

# Register the built-in schemes by import, but don't expose this in the API.
# Users should import specific schemes explicitly.
from . import schemes as _schemes
