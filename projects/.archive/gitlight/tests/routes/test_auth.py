#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test auth routes and decorators
'''
# Python / Flask Imports
import pytest


def test_access_check(client):
    '''
    Test access_required decorator
    '''
    pass


def test_get_login(client):
    '''
    Test user_login and session
    '''
    response = client.get('/login')
    assert b'<form' in response.data


@pytest.mark.broken
def test_post_login_fail(client):
    '''
    Test user_login and session
    '''
    response = client.post('/login',
            follow_redirects=True,
            data={
                'user': 'tester',
                'pass': 'invalid',
            })
    assert b'Invalid' in response.data


def test_post_login_pass(client):
    '''
    Test user_login and session
    '''
    #assert b'' in response.data
    #assert redirect in response.headers
    pass


def test_logout(client):
    '''
    Test user_logout and session
    '''
    pass


def test_user(client):
    '''
    Test show user profile
    '''
    pass
