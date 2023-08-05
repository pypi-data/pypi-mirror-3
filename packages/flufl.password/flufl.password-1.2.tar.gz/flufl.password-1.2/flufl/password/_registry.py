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

"""Scheme registry."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'BadPasswordSchemeError',
    'lookup',
    'register',
    ]


_registry = {}



class BadPasswordSchemeError(Exception):
    """An unknown password scheme tag was given."""



def register(scheme_class):
    """Register a scheme by its tag.

    This is intended to be used as a class descriptor.

    :param scheme_class: A password scheme.
    :type scheme_class: A class which has a `TAG` attribute.  The tag may
        contain space-separated words with additional information, but the
        scheme will be registered using the first word as the key.
    :return: scheme_class
    """
    key = scheme_class.TAG.split()[0]
    _registry[key] = scheme_class
    return scheme_class


def lookup(tag):
    """Return a scheme class by its tag.

    :param tag: The tag to search for.  The tag may contain space-separated
        words with additional information, but the scheme will be looked up
        using the first word as the key.
    :type tag: string
    :return: The matching scheme class.
    :rtype: class
    :raises BadPasswordSchemeError: when the named scheme can't be found.
    """
    key = tag.split()[0]
    try:
        return _registry[key]
    except KeyError:
        raise BadPasswordSchemeError(tag)
