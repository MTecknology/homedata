#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the utils library.
'''
# Python / Flask Imports
import six

# GitLight Imports
from gitlight.libs import utils


def test_encode(app):
    '''
    Verify encoding/decoding works as expected.
    '''
    with app.test_request_context():
        value = {'test': 'string'}
        assert isinstance(utils.encode({'foo': 'bar'}), six.string_types)
        assert utils.encode('foo') != utils.encode('bar')


def test_decode(app):
    '''
    Verify encoding/decoding works as expected.
    '''
    with app.test_request_context():
        value = utils.encode({'test': '^'})
        assert isinstance(utils.decode(value), dict)
        assert utils.decode('xyz{}'.format(value)) == None
        assert utils.encode({'test': '!'}) != value
        assert utils.decode(value)['test'] == '^'

        assert utils.decode('x{}'.format(utils.encode({'foo': 'bar'}))) is None


def test_uuid():
    '''
    Test uuid function
    '''
    assert isinstance(utils.uuid(5), six.string_types)
    assert utils.uuid(5) != utils.uuid(5)
    assert len(utils.uuid(7)) == 7
    assert len(utils.uuid(99)) == 32


def test_hash():
    '''
    Test hash function
    '''
    assert isinstance(utils.hash('foo'), six.string_types)
    assert utils.hash('foo') == 'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'
