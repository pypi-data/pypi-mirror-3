from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.datastructures import SortedDict
from django.utils.crypto import constant_time_compare
from django.utils.translation import ugettext_noop as _

import scrypt


class ScryptPasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the scrypt algorithm

    The py-scrypt library must be installed separately. That library
    depends on native C code and might cause portability issues.
    """

    algorithm = "scrypt"
    library = ("scrypt")
    Nexp = 14  # N == 2 ** 14 == 16384
    r = 8
    p = 1
    buflen = 64

    def verify(self, password, encoded):
        """
        Checks if the given password is correct
        """
        algorithm, salt, Nexp, r, p, buflen, h = encoded.split('$')
        assert algorithm == self.algorithm
        # TODO: buflen is an experimental proposal in py-scrypt
        hashp = self.encode(password, salt, int(Nexp), int(r), int(p))
        return constant_time_compare(encoded, hashp)

    def encode(self, password, salt, Nexp=None, r=None, p=None, buflen=None):
        """
        Creates an encoded hash string from password, salt and optional
        parameters.

        password is the user's chosen password as a string
        salt is a string, django provides a 12-character random string from
            [a-zA-Z0-9] by default
        Nexp is the exponent for N such that N = 2 ** Nexp, Nexp = 14 means
            N = 2 ** 14 = 16384 which is the value passed to the
            Scrypt module. Must be a positive integer >= 1.
        r is the r-value passed to Scrypt
        p is the p-value passed to Scrypt
        buflen is the length of the returned hash in bytes (not currently
            implemented in underlying module)

        Returns "scrypt$salt$Nexp$r$p$buflen$hash" where hash is a base64
        encoded byte string (64-bytes by default)
        """
        assert password
        assert salt and '$' not in salt
        hashed = [self.algorithm]
        hashed.append(salt)
        if not Nexp:
            Nexp = self.Nexp
        if not r:
            r = self.r
        if not p:
            p = self.p
        if not buflen:
            buflen = self.buflen
        # TODO: buflen is an experimental proposal in py-scrypt
        buflen = self.buflen
        hashed.append(str(Nexp))
        hashed.append(str(r))
        hashed.append(str(p))
        hashed.append(str(buflen))
        h = scrypt.hash(password, salt, 2 ** Nexp, r, p)
        hashed.append(h.encode('base64').strip())
        return "$".join(hashed)

    def safe_summary(self, encoded):
        """
        Returns a summary of safe values

        The result is a dictionary and will be used where the password field
        must be displayed to construct a safe representation of the password.
        """
        algorithm, salt, Nexp, r, p, buflen, h = encoded.split('$')
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('Nexp'), Nexp),
            (_('r'), r),
            (_('p'), p),
            (_('buflen'), buflen),
            (_('hash'), mask_hash(h)),
        ])
