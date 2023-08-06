# -*- coding: utf-8 -*-

from __future__ import with_statement
from django.conf.global_settings import PASSWORD_HASHERS as default_hashers
from django.contrib.auth.hashers import (
    is_password_usable, check_password, make_password,
    get_hasher, load_hashers, UNUSABLE_PASSWORD)
from django.utils.unittest import TestCase, skipUnless
from django.utils.translation import ugettext_noop as _

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
        self.bad_password = 'letmeinz'
        self.expected_hash_prefix = "scrypt"

    def test_verify_bad_passwords_fail(self):
        """Test verify method causes failure on mismatched passwords"""
        encoded = make_password(self.password)
        self.assertFalse(check_password(self.bad_password, encoded))

    def test_verify_passwords_match(self):
        """Test verify method functions via check_password"""
        encoded = make_password(self.password)
        self.assertTrue(check_password(self.password, encoded))

    def test_encoder_hash_less_than_128_characters(self):
        """Test that returned encoded hash is less than db limit of 128 characters"""
        encoded = make_password(self.password)
        self.assertTrue(len(encoded) < 128)

    def test_encoder_specified_scrypt_hasher(self):
        """Test hasher is obtained by name"""
        encoded = make_password('letmein', hasher='scrypt')
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

    def test_class_algorithm_string_matches_expected(self):
        """Test django_scrypt algorithm string matches expected value 'scrypt'"""
        self.assertEqual(ScryptPasswordHasher.algorithm, self.expected_hash_prefix)

    def test_no_upgrade_on_incorrect_pass(self):
        self.assertEqual('scrypt', get_hasher('default').algorithm)
        for algo in ('sha1', 'md5'):
            encoded = make_password('letmein', hasher=algo)
            state = {'upgraded': False}

            def setter():
                state['upgraded'] = True
            self.assertFalse(check_password(self.bad_password, encoded, setter))
            self.assertFalse(state['upgraded'])

    def test_no_upgrade(self):
        encoded = make_password('letmein')
        state = {'upgraded': False}

        def setter():
            state['upgraded'] = True
        self.assertFalse(check_password(self.bad_password, encoded, setter))
        self.assertFalse(state['upgraded'])

    def test_upgrade(self):
        self.assertEqual('scrypt', get_hasher('default').algorithm)
        for algo in ('sha1', 'md5'):
            encoded = make_password('letmein', hasher=algo)
            state = {'upgraded': False}

            def setter(password):
                state['upgraded'] = True
            self.assertTrue(check_password('letmein', encoded, setter))
            self.assertTrue(state['upgraded'])
