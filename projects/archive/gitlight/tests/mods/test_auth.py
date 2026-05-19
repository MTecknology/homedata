#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the utils library.
'''
# Python / Flask Imports
import unittest.mock

# GitLight Imports
from gitlight.mods import auth
from gitlight.api import get_user

# Test Data
from tests.data.users import TEST_USERS


def test_valid_credentials(app):
    '''
    Test validate_credentials function of auth module against valid credentials.
    '''
    with app.test_request_context():
        with unittest.mock.patch('gitlight.mods.auth.get_user', return_value=TEST_USERS['tester']['dict']):
            assert auth.validate_credentials('tester', 'foo')[0] == True


def test_invalid_credentials(app):
    '''
    Test validate_credentials function of auth module against invalid credentials.
    '''
    with app.test_request_context():
        with unittest.mock.patch('gitlight.mods.auth.get_user', return_value=TEST_USERS['tester']['dict']):
            assert auth.validate_credentials('tester', 'invalid')[0] == False
            assert auth.validate_credentials('invalid', 'foo')[0] == False
            assert auth.validate_credentials('invalid', None)[0] == False
            assert auth.validate_credentials(None, 'foo')[0] == False


def test_missing_credentials(app):
    '''
    Test validate_credentials function of auth module against missing credentials.
    '''
    with app.test_request_context():
        with unittest.mock.patch('gitlight.mods.auth.get_user', return_value=None):
            assert auth.validate_credentials('tester', 'invalid')[0] == False


def test_get_user():
    '''
    Test get_user function of auth module.
    '''
    for user, data in TEST_USERS.items():
        print('Testing user: {}'.format(user))
        with unittest.mock.patch('gitlight.libs.git.read_file', return_value=data['blob']):
            resp = get_user.action({'username': user})
        with unittest.mock.patch('gitlight.libs.message_queue.send', return_value=resp):
            assert auth.get_user(user) == data['dict']


def test_get_user_invalid():
    '''
    Test get_user function of auth module with an invalid mq response.
    '''
    with unittest.mock.patch('gitlight.libs.message_queue.send', return_value=None):
        assert auth.get_user('foo') is False
