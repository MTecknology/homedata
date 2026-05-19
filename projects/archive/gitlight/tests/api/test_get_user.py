#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the utils library.
'''
# Python / Flask Imports
import six
import unittest.mock

# GitLight Imports
from gitlight.api.get_user import action

# Test Data
from tests.data.users import TEST_USERS


def test_action():
    '''
    Test get_user API function handles all user.yml mistakes.
    '''
    for user, data in TEST_USERS.items():
        print('Testing user: {}'.format(user))
        with unittest.mock.patch('gitlight.libs.git.read_file', return_value=data['blob']):
            result = action({'username': user})
            if data['issue_expected']:
                assert result['success'] == False
                assert isinstance(result['body'], six.string_types)
                assert result['body'] == data['issue_read-result']
            else:
                assert result['success'] == True
                assert isinstance(result['body'], dict)
                assert result['body'].get('username') == user


def test_invalid():
    '''
    Test get_user API function handles incorrect data.
    '''
    assert action('fuzz')['body'] == 'bad message data'


def test_empty():
    '''
    Test get_user API function handles missing data.
    '''
    assert action({})['body'] == 'no username provided'
