# -*- coding: utf-8 -*-
"""
    werkzeug.security test
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD license.
"""
import os
from werkzeug.security import check_password_hash, generate_password_hash, \
     safe_join


def test_password_hashing():
    """Test the password hashing and password hash checking"""
    hash1 = generate_password_hash('default')
    hash2 = generate_password_hash(u'default', method='sha1')
    assert hash1 != hash2
    assert check_password_hash(hash1, 'default')
    assert check_password_hash(hash2, 'default')
    assert hash1.startswith('sha1$')
    assert hash2.startswith('sha1$')

    fakehash = generate_password_hash('default', method='plain')
    assert fakehash == 'plain$$default'
    assert check_password_hash(fakehash, 'default')

    mhash = generate_password_hash(u'default', method='md5')
    assert mhash.startswith('md5$')
    assert check_password_hash(mhash, 'default')

    legacy = 'md5$$c21f969b5f03d33d43e04f8f136e7682'
    assert check_password_hash(legacy, 'default')

    legacy = u'md5$$c21f969b5f03d33d43e04f8f136e7682'
    assert check_password_hash(legacy, 'default')


def test_safe_join():
    """Test the safe joining helper"""
    assert safe_join('foo', 'bar/baz') == os.path.join('foo', 'bar/baz')
    assert safe_join('foo', '../bar/baz') is None
    if os.name == 'nt':
        assert safe_join('foo', 'foo\\bar') is None
