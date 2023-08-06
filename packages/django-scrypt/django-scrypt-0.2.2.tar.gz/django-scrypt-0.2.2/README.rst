Django-Scrypt
*************

*Django-Scrypt* is a *Scrypt*-enabled password hasher for *Django* ver. 1.4.

.. warning::

   The encoded hash format has changed in version 0.2.0. This change is
   backwards incompatible. Please read the notice in the Caveats_ section.

*Scrypt* is a sequential memory-hard key derivation function. This software allows *Django* to access low-level bindings of the *Scrypt* key derivation function via *Py-Scrypt*.

Installation
============

.. warning::

   This is alpha software under active development and as such it is not suitable for production use. It was tested only
   on **Python 2.6/2.7 on a 32-bit Mac**. It probably will not run on Python
   2.5 since *Py-Scrypt* doesn't run on interpreters earlier than 
   Python 2.6.

Installing *Django-Scrypt* into your system-wide Python's ``site-packages`` directory is not recommended. Instead, use `virtualenv <http://www.virtualenv.org/en/latest/index.html>`_ and `virtualenvwrapper <http://www.doughellmann.com/docs/virtualenvwrapper/>`_ to create isolated virtual Python environments and then install this software into the isolated *virtualenv*'s ``site-packages`` directory.

.. note::

   You should install `Django 1.4 <http://pypi.python.org/pypi/Django>`_ and `py-scrypt <http://pypi.python.org/pypi/scrypt>`_ prior to installing
   *Django-Scrypt*

Using source tarballs
---------------------

1. Download the *Django-Scrypt* source tarball from Pypi (`Python
   Package Index <http://en.wikipedia.org/wiki/Python_Package_Index>`_)

       http://pypi.python.org/pypi/django-scrypt/

2. Decompress it and make it your working directory::

       $ tar zxvf django-scrypt-0.2.2.tar.gz
       $ cd django-scrypt-0.2.2

3. Install it into your ``site-packages`` directory (if you install to the
   system's ``site-packages`` you will probably need to be root or you will
   probably need to use ``sudo`` to copy into protected directories)::

       $ python setup.py install

4. Test your installation::

       $ python setup.py test

Using Pip and Pypi
------------------

If you are installing to the system-wide ``site-packages`` then you
will probably need to be root or you will probably need to use ``sudo``.

1. Use the ``pip`` command to install from Pypi::

       $ pip install django-scrypt

Using a Clone from BitBucket
----------------------------

Since this is nascent software, you may want to get the most recent
development version.

1. Use `Mercurial <http://mercurial.selenic.com/>`_ to clone the
   repository::

       $ hg clone https://bitbucket.org/kelvinwong_ca/django-scrypt
       $ cd django-scrypt

2. Install it into your ``site-packages`` (if you install it in your system's
   ``site-packages`` you will probably need to be root or you will probably
   need to use ``sudo``)::

       $ python setup.py install

3. Test your installation (seriously, *please* do this)::

       $ python setup.py test

Keep in mind that the development tip will always be the least stable and the
least tested version of the software. Please excuse the mess.

Basic Usage
===========

.. warning::

   This software depends on *Py-Scrypt* version 0.5.5 to reveal
   the *Scrypt* hashing function. Unfortunately, it contains a bug
   that can result in incorrect hashing when run on 64-bit Linux systems. View
   the *Py-Scrypt* issue tracker for the latest information on this issue. [#]_

.. [#] See *Py-Scrypt* `Issue 6 <https://bitbucket.org/mhallin/py-scrypt/issue/6/hash-dies-with-sigfpe-when-passing-r-or-p>`_

To use *Scrypt* as your default password storage algorithm in *Django 1.4*,
install it and make the following changes. In your *Django 1.4* application's
``settings.py`` file, modify the ``PASSWORD_HASHERS`` tuple (or add it if it
is missing) to include ``ScryptPasswordHasher`` as the first hasher in the
tuple. It needs to be at the very top.

For example::

  PASSWORD_HASHERS = (
    'django_scrypt.hashers.ScryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
  )

You have now changed your app to use *Scrypt* as the default storage
algorithm. As users login to your system they will automatically upgrade their hashed passwords to *Scrypt* hashes.

.. note::

   You need to keep the other hasher entries in this list or else *Django*
   won't be able to upgrade the passwords!

Scrypt Parameters
-----------------

*Scrypt* takes three tuning parameters: ``N``, ``r`` and ``p``.
They affect memory usage and running time. Memory usage is approximately
``128 * r * N`` bytes. [#]_ These are the default values::

   Nexp = lb(N) = 14, r = 8 and p = 1
   where lb is logarithm base 2

*Django-Scrypt* stores ``Nexp`` in the encoded hash, but not ``N``. The positive integer ``Nexp`` is the exponent used to generate ``N`` which is calculated as needed (``N = 2 ** Nexp``). Doing this saves space in the database row. These default values lead to *Scrypt* using ``128 * 8 * 2 ** 14 = 16M`` bytes of memory.

The values of ``N``, ``r`` and ``p`` affect running time proportionately; however, ``p`` can be used to independently tune the running time since it has a smaller influence on memory usage.

The final parameter ``buflen`` has been proposed for *Py-Scrypt* but is not implemented. The value will be used to change the size of the returned hash. Currently, *Py-Scrypt's* ``hash`` function returns a message digest of length 64-bytes or 512-bits.

.. [#] Adapted from Falko Peters' `Crypto.Scrypt package for Haskell  <http://hackage.haskell.org/packages/archive/scrypt/0.3.2/doc/html/Crypto-Scrypt.html>`_

.. _Caveats:

Caveats
=======

Hash Format Changes As 'N' Removed
----------------------------------

In an attempt to shorten the length of the encoded hash, I removed the
``N``-value and replaced it with an ``N``-exponent value named ``Nexp``.
The reason for this is that ``N`` must be a power of 
two {2, 4, 8, ... 16384, ...etc...} and those digits take up room in a 
128 character hash storage space. It makes more sense to me to store the exponent and just make the actual integer on the fly.

       ``N == 16384 == 2 ** 14 therefore Nexp == 14``

The old encoded hash format that got stored in *Django's* database was

        ``scrypt$salt$16384$8$1$64$Base64Hash==``

The new and shorter encoded hash format is

        ``scrypt$salt$14$8$1$64$Base64Hash==``

The good news is that "14" is three characters shorter than "16384". The bad news
is that this introduces a backwards incompatible change as of version 0.2.0.

If you see your application generating *HTTP 500 Server Errors* with an *Exception* raised with
*error: 'hash parameters are wrong (r*p should be < 2**30, and N should
be a power of two > 1)'* then you should suspect that an old hash is telling
*Scrypt* to use ``N = 2 ** 16384`` which is way, way, way too large. The
solution is to replace the 16384 in the old hashes with 14. You might have to alter your database manually or write some custom code to fix this change.

Django Password Field Character Length Limits
---------------------------------------------

By default, *Django* limits password field lengths to 128 characters. Using
the default settings in *Django-Scrypt* with *Django's* salting
implementation should yield encoded hashes less than 128 characters (approx 119 characters); however, if you override the ``ScryptPasswordHasher``
class variables you might end up overflowing the default password field.

The solution is to increase the size of the password field using SQL. You
should consult your database documentation for the correct commands necessary to alter your database.

Bugs! Help!!
============

If you find any bugs in this software please report them via the BitBucket
issue tracker [#]_ or send an email to code@kelvinwong.ca. Any serious
security bugs should be reported via email only.

.. [#] Django-Scrypt issue tracker https://bitbucket.org/kelvinwong_ca/django-scrypt/issues

Thank-you
=========

Thank-you for taking the time to evaluate this software. I appreciate
receiving feedback on your experiences using it and I welcome code
contributions and development ideas.

http://www.kelvinwong.ca/coders

Thanks to Dr Colin Percival for his original *Scrypt* software [#]_,
also to Magnus Hallin for the *Py-Scrypt* Python module [#]_.

.. [#] Visit http://www.tarsnap.com/scrypt.html
.. [#] Visit http://pypi.python.org/pypi/scrypt/
