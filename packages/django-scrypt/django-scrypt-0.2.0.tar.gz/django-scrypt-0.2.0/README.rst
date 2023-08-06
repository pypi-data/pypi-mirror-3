Django-Scrypt
*************

Django-Scrypt is a Scrypt-enabled password hasher for Django 1.4

.. warning::

   The encoded hash format has changed in version 0.2.0. This change is
   backwards incompatible. Please read the notice in the Caveat section.

.. warning::

   This is alpha software under active development. It was tested only
   on **Python 2.7**. It probably will not run on Python 2.5 since
   ``py-scrypt`` doesn't run on interpreters earlier than Python 2.6.

Installation
============

.. note::

   You need to install Django 1.4 and ``py-scrypt`` prior to installing
   Django-Scrypt

Using source tarballs
---------------------

1. Download the source tarball for Django-Scrypt from Pypi

       http://pypi.python.org/pypi/django-scrypt/

2. Decompress it and make it your working directory::

       $ tar zxvf django-scrypt-0.2.0.tar.gz
       $ cd django-scrypt-0.2.0

3. Install it into your site-packages (if you install to the system's site
   packages you will probably need to be root or you will probably need to use
   ``sudo``)

       ``$ python setup.py install``

4. Test your installation

       ``$ python setup.py test``

Using Pip and Pypi
------------------

If you are installing to the system-wide site-packages then you will probably
need to be root or you will probably need to use ``sudo``.

1. Use the ``pip`` command to install from Pypi

       ``$ pip install django-scrypt``

Basic Usage
===========

.. warning::

   This software depends on ``py-scrypt`` version 0.5.5 to reveal
   the Scrypt hashing function. Unfortunately, ``py-scrypt`` contains a bug
   that can result in incorrect hashing when run on 64-bit Linux systems. View
   the ``py-scrypt`` issue tracker for the latest information on this issue. [#]_

.. [#] See py-scrypt `Issue 6 <https://bitbucket.org/mhallin/py-scrypt/issue/6/hash-dies-with-sigfpe-when-passing-r-or-p>`_

To use Scrypt as your default password storage algorithm in Django 1.4,
install it and make the following changes. In your Django 1.4 application
*settings.py* file, modify (or add it if it is missing) the
``PASSWORD_HASHERS`` tuple to include ``ScryptPasswordHasher`` as the first
hasher in the tuple. It needs to be at the top.

For example::

  PASSWORD_HASHERS = (
    'django_scrypt.hashers.ScryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
  )

.. note::

   You need to keep the other hasher entries in this list or else Django
   won't be able to upgrade the passwords!

You have now changed your app to use Scrypt as the default storage algorithm.
As users login to your system they will automatically upgrade to use Scrypt
hashes.

Caveat
======

Hash Format Changes As N Removed
--------------------------------

In an attempt to shorten the length of the encoded hash, I removed the
N-value and replaced it with an N-exponent value named Nexp. The reason for
this is that N must be a power of two {2, 4, 6, ... 16384, ...etc...} and
those digits take up room in a 128 character hash storage space. It makes
more sense to me to store the exponent and just make the actual integer on
the fly.

       ``N == 16384 == 2 ** 14 therefore Nexp == 14``

The bad news is that this introduces a backward incompatible change as of
version 0.2.0.

Django Password Field Character Length Limits
---------------------------------------------

By default, Django limits password field lengths to 128 characters. Using the
default settings in Django-Scrypt with the Django salting implementation
should yield encoded hashes less than 128 characters; however, if you override
the ScryptPasswordHasher class variables you might end up overflowing the
field.

The solution is to increase the size of the password field using SQL. You
should consult your database documentation for the correct commands.

Bugs! Help!!
============

If you find bugs please report them to the BitBucket issue tracker or send
me an email to code@kelvinwong.ca. Any serious security bugs should be
reported via email.

https://bitbucket.org/kelvinwong_ca/django-scrypt/issues

Thank-you
=========

Thank-you for taking the time to evaluate this software. I appreciate
receiving feedback on your experiences with it and I welcome code
contributions and development ideas.

http://www.kelvinwong.ca/coders

Thanks to Dr Colin Percival for his original Scrypt software [#]_,
also to Magnus Hallin for the py-scrypt Python module [#]_.

.. [#] Visit http://www.tarsnap.com/scrypt.html
.. [#] Visit http://pypi.python.org/pypi/scrypt/
