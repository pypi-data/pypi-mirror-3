# -*- coding: utf-8 -*-

from __future__ import with_statement
from django.conf.global_settings import PASSWORD_HASHERS as default_hashers
from django.contrib.auth.hashers import (
    is_password_usable, check_password, make_password,
    get_hasher, load_hashers, UNUSABLE_PASSWORD)
from django.utils.unittest import TestCase, skipUnless
from django.utils.translation import ugettext_noop as _

import django_scrypt
from django_scrypt.hashers import ScryptPasswordHasher

try:
    import scrypt
except ImportError:
    scrypt = None


@skipUnless(scrypt, "Uninstalled scrypt module needed to generate hash")
class TestScrypt(TestCase):

    def setUp(self):
        scrypt_hashers = ("django_scrypt.hashers.ScryptPasswordHasher",) + default_hashers
        load_hashers(password_hashers=scrypt_hashers)
        self.password = 'letmein'
        self.unicode_text = '\xe1\x93\x84\xe1\x93\x87\xe1\x95\x97\xe1\x92\xbb\xe1\x92\xa5\xe1\x90\x85\xe1\x91\xa6'.decode('utf-8')
        self.bad_password = 'letmeinz'
        self.expected_hash_prefix = "scrypt"
        self.old_format_encoded_hash = "scrypt$FYY1dftUuK0b$16384$8$1$64$/JYOBEED7nMzJgvlqfzDj1JKGVLup0eYLyG39WA2KCywgnB1ubN0uzFYyaEQthINm6ynjjqr+D+U\nw5chi74WVw=="
        self.old_format_fix_encoded_hash = "scrypt$FYY1dftUuK0b$14$8$1$64$/JYOBEED7nMzJgvlqfzDj1JKGVLup0eYLyG39WA2KCywgnB1ubN0uzFYyaEQthINm6ynjjqr+D+U\nw5chi74WVw=="
        self.encoded_hash = "scrypt$gwQg9TZ3eyub$14$8$1$64$lQhi3+c0xkYDUj35BvS6jVTlHRAH/RS4nkpd1tKMc0r9PcFyjCjPj1k9/CkSCRvcTvHiWfFYpHfB\nZDCHMNIeHA=="

    def test_version_string_set(self):
        """Test for version string on package"""
        self.assertTrue(type(django_scrypt.__version__), str)
        self.assertTrue(len(django_scrypt.__version__) > 0)

    def test_encoder_default_hash_less_than_128_characters(self):
        """Test that returned encoded hash is less than db limit of 128 characters"""
        encoded = make_password(self.password)
        self.assertTrue(len(encoded) < 128)

    def test_encoder_accepts_unicode(self):
        """Test that passwords can be Unicode"""
        encoded = make_password(self.unicode_text)
        self.assertTrue(check_password(self.unicode_text, encoded))

    def test_encoder_specified_scrypt_hasher(self):
        """Test hasher is obtained by name"""
        encoded = make_password(self.password, hasher='scrypt')
        self.assertTrue(check_password(self.password, encoded))

    def test_encoder_hash_usable(self):
        """Test encoder returns usable hash string"""
        encoded = make_password(self.password)
        self.assertTrue(is_password_usable(encoded))

    def test_encoder_hash_starts_with_algorithm_string(self):
        """Test that encoded hash string has correct prefix with first separator"""
        encoded = make_password(self.password)
        self.assertTrue(encoded.startswith(self.expected_hash_prefix + "$"))

    def test_encoder_hash_has_required_sections(self):
        """Test encoder returns hash with required sections"""
        encoded = make_password(self.password)
        algorithm, salt, Nexp, r, p, buflen, h = encoded.split('$')
        self.assertEqual(algorithm, self.expected_hash_prefix)
        self.assertTrue(len(salt))
        self.assertTrue(Nexp.isdigit())
        self.assertTrue(r.isdigit())
        self.assertTrue(p.isdigit())
        self.assertTrue(buflen.isdigit())
        self.assertTrue(len(h))

    def test_safe_summary_has_required_sections(self):
        """Test safe_summary returns string with required informative sections"""
        encoded = make_password(self.password)
        hasher = get_hasher('scrypt')
        d = hasher.safe_summary(encoded)
        self.assertEqual(d[_('algorithm')], self.expected_hash_prefix)
        self.assertTrue(len(d[_('salt')]))
        self.assertTrue(d[_('Nexp')].isdigit())
        self.assertTrue(d[_('r')].isdigit())
        self.assertTrue(d[_('p')].isdigit())
        self.assertTrue(d[_('buflen')].isdigit())
        self.assertTrue(len(d[_('hash')]))

    def test_verify_bad_passwords_fail(self):
        """Test verify method causes failure on mismatched passwords"""
        encoded = make_password(self.password)
        self.assertFalse(check_password(self.bad_password, encoded))

    def test_verify_passwords_match(self):
        """Test verify method functions via check_password"""
        encoded = make_password(self.password)
        self.assertTrue(check_password(self.password, encoded))

    def test_verify_default_hash_format_usable(self):
        """Test encoded format passes good password"""
        self.assertTrue(check_password(self.password, self.encoded_hash))

    def test_verify_old_hash_format_raises_error(self):
        """Test that deprecated, old encoded hash format raises an Exception

        The old format hashes store N == 16384 whereas new format store Nexp == 14.
        The fix is to replace 16384 with 14 in each hash.
        """
        with self.assertRaises(Exception) as cm:
            check_password(self.password, self.old_format_encoded_hash)
        self.assertEqual(
            "hash parameters are wrong (r*p should be < 2**30, and N should be a power of two > 1)",
            str(cm.exception))

    def test_verify_old_hash_format_fixable(self):
        """Test deprecated encoded format can be fixed by swapping Nexp for N

        Specifically, replace 16384 with 14 at position 3 of the encoded hash
        """
        self.assertTrue(check_password(self.password, self.old_format_fix_encoded_hash))

    def test_class_algorithm_string_matches_expected(self):
        """Test django_scrypt algorithm string matches expected value 'scrypt'"""
        self.assertEqual(ScryptPasswordHasher.algorithm, self.expected_hash_prefix)

    def test_no_upgrade_on_incorrect_pass(self):
        self.assertEqual('scrypt', get_hasher('default').algorithm)
        for algo in ('sha1', 'md5'):
            encoded = make_password(self.password, hasher=algo)
            state = {'upgraded': False}

            def setter():
                state['upgraded'] = True
            self.assertFalse(check_password(self.bad_password, encoded, setter))
            self.assertFalse(state['upgraded'])

    def test_no_upgrade(self):
        encoded = make_password(self.password)
        state = {'upgraded': False}

        def setter():
            state['upgraded'] = True
        self.assertFalse(check_password(self.bad_password, encoded, setter))
        self.assertFalse(state['upgraded'])

    def test_upgrade(self):
        self.assertEqual('scrypt', get_hasher('default').algorithm)
        for algo in ('sha1', 'md5'):
            encoded = make_password(self.password, hasher=algo)
            state = {'upgraded': False}

            def setter(password):
                state['upgraded'] = True
            self.assertTrue(check_password(self.password, encoded, setter))
            self.assertTrue(state['upgraded'])
