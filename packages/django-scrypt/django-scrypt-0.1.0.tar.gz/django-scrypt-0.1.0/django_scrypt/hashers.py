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
    N = 16384
    r = 8
    p = 1
    buflen = 64

    def verify(self, password, encoded):
        """
        Checks if the given password is correct
        """
        algorithm, salt, N, r, p, buflen, h = encoded.split('$')
        assert algorithm == self.algorithm
        # TODO: bufflen is an experimental proposal of py-scrypt, not supported in this version
        hashp = self.encode(password, salt, int(N), int(r), int(p))
        return constant_time_compare(encoded, hashp)

    def encode(self, password, salt, N=None, r=None, p=None, buflen=None):
        """
        Creates an encoded database value

        The result is normally formatted as "algorithm$salt$hash" and
        must be fewer than 128 characters.
        """
        assert password
        assert salt and '$' not in salt
        hashed = [self.algorithm]
        hashed.append(salt)
        if not N:
            N = self.N
        if not r:
            r = self.r
        if not p:
            p = self.p
        if not buflen:
            buflen = self.buflen
        # TODO: bufflen is an experimental proposal of py-scrypt, not supported in this version
        buflen = self.buflen
        hashed.append(str(N))
        hashed.append(str(r))
        hashed.append(str(p))
        hashed.append(str(buflen))
        h = scrypt.hash(password, salt, N, r, p)
        hashed.append(h.encode('base64').strip())
        return "$".join(hashed)

    def safe_summary(self, encoded):
        """
        Returns a summary of safe values

        The result is a dictionary and will be used where the password field
        must be displayed to construct a safe representation of the password.
        """
        algorithm, salt, N, r, p, buflen, h = encoded.split('$')
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('N'), N),
            (_('r'), r),
            (_('p'), p),
            (_('buflen'), buflen),
            (_('hash'), mask_hash(h)),
        ])
