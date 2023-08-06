================================
Using the flufl.password package
================================

This package comes with a number of password hashing schemes.  Some are more
secure, while others provide for useful debugging.  A hashed password follows
the syntax promoted in `RFC 2307`_ (as best I can tell), having a basic format
of ``{scheme}hashed_password``.


Hashing a password
==================

You can create a secure hashed password using the default scheme, which
includes random data.

    >>> from flufl.password import make_secret
    >>> show(make_secret('my password'))
    {SSHA}...

You can also create a hashed password using one of the other built-in
schemes.

    >>> from flufl.password.schemes import SHAPasswordScheme
    >>> show(make_secret('my password', SHAPasswordScheme))
    {SHA}ovj3-hlaCAoipokEHaqPIET58zY=


Available schemes
-----------------

There are several built-in schemes to choose from, which run the gamut from
useful for debugging to variously higher levels of security.

 * The *no password* scheme throws away the password and always returns the
   empty string, but with a properly formatted password.

   >>> from flufl.password.schemes import NoPasswordScheme
   >>> show(make_secret('my password', NoPasswordScheme))
   {NONE}

 * The *clear text* scheme returns the original password in clear text, but
   properly formatted.

   >>> from flufl.password.schemes import ClearTextPasswordScheme
   >>> show(make_secret('my password', ClearTextPasswordScheme))
    {CLEARTEXT}my password

 * The *SHA1* password scheme encodes the SHA1 hash of the password.

   >>> show(make_secret('my password', SHAPasswordScheme))
   {SHA}ovj3-hlaCAoipokEHaqPIET58zY=

 * The *salted SHA1* scheme adds a random salt to the password's digest.

   >>> from flufl.password.schemes import SSHAPasswordScheme
   >>> show(make_secret('my password', SSHAPasswordScheme))
   {SSHA}...

 * There is an `RFC 2898`_ password encoding scheme.

   >>> from flufl.password.schemes import PBKDF2PasswordScheme
   >>> show(make_secret('my password', PBKDF2PasswordScheme))
   {PBKDF2 SHA 2000}...


Custom schemes
--------------

It's also easy enough to create your own scheme.  It must implement a static
`make_secret()` method, which you can inherit from a common base class.  The
class must also have a `TAG` attribute which gives the unique name of this
hashing scheme.

The scheme should be registered so that it can be found by its tag for
verification purposes.  This can be done using the `@register` descriptor.
::

    >>> from codecs import getencoder
    >>> from flufl.password import register
    >>> from flufl.password.schemes import PasswordScheme

    >>> @register
    ... class MyScheme(PasswordScheme):
    ...     TAG = 'CAESAR'
    ...     @staticmethod
    ...     def make_secret(password):
    ...         # In Python 3, this is a string-to-string encoding.  The
    ...         # caller already turned `password` into a byte string, so
    ...         # we have to pass it back through a string to rotate it.
    ...         # We also can't just call .encode('rot_13') on the string
    ...         # because Python 3.2 chokes on the returned string (it expects
    ...         # a bytes object to be returned).  Sigh.
    ...         as_string = password.decode('utf-8')
    ...         encoder = getencoder('rot_13')
    ...         return encoder(as_string)[0].encode('utf-8')

    >>> show(make_secret('my password', MyScheme))
    {CAESAR}zl cnffjbeq

Hashed passwords are always bytes.

    >>> isinstance(make_secret('my password', MyScheme), bytes)
    True


Verifying a password
====================

When the user entered their original password, you hashed it using one of the
schemes mentioned above.  You are only storing this hashed password in your
database.

The user now wants to log in, so she provides you with her plain text
password.  You want to see if they match.

The easiest way to do this is to give both the plain text password the user
just typed, and the hash password you have in your database.

    >>> from flufl.password import verify
    >>> verify(b'{SHA}ovj3-hlaCAoipokEHaqPIET58zY=', 'my password')
    True

Of course, if they enter the wrong password, it does not verify.

    >>> verify(b'{SHA}ovj3-hlaCAoipokEHaqPIET58zY=', 'your password')
    False

Your custom hashing scheme must implement the `check_response()` API in order
to support password verification.  The `PasswordScheme` base class supports
the most obvious implementation of this, which serves for most schemes.  For
example, the Caesar scheme does not need to implement a `check_response()`
method.

    >>> verify(b'{CAESAR}zl cnffjbeq', 'my password')
    True


User-friendly passwords
=======================

This package also provides a convenient utility for generating *user friendly*
passwords.  These passwords gather random input and translate them into pairs
of vowel-consonant (or consonant-vowel) syllables.  It then strings together
enough of these syllables to match the requested password length.  In theory,
this produces relatively secure passwords that are easier to pronounce and
remember.  The security claims of these generated passwords have not been
evaluated.

    >>> from flufl.password import generate
    >>> my_password = generate(10)
    >>> len(my_password)
    10
    >>> sum(1 for c in my_password if c in 'aeiou')
    5
    >>> sum(1 for c in my_password if c not in 'aeiou')
    5


.. _`RFC 2307`: http://www.faqs.org/rfcs/rfc2307.html
.. _`RFC 2898`: http://www.faqs.org/rfcs/rfc2898.html
