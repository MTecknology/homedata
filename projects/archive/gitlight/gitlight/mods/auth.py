#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Handle authentication and authorization.
'''
# Python / Flask Imports
import flask
import flask_login

# GitLight Imports
from gitlight.libs import message_queue
from gitlight.libs import utils

class User(flask_login.UserMixin):
    '''
    Simple class to store user attributes
    '''
    def __init__(self, username, gecos_fields, passwords=None):
        self.id = username
        self.passwords = passwords
        self.gecos_fields = gecos_fields


def get_user(username, with_auth=False):
    '''
    Returns a dictionary of user data, or None if user not found.
    '''
    resp = message_queue.send('/mq', {
        'action': 'get_user',
        'message_id': utils.uuid(4),
        'username': username,
        })
    if not resp or not isinstance(resp, dict):
        return False
    if not resp.get('success', False):
        return False

    rdata = resp.get('body', {})

    user = User(
            username=rdata.get('username', None),
            gecos_fields=rdata.get('gecos_fields', {}),
            passwords=rdata.get('passwords', []))

    if not with_auth:
        user.passwords = []

    return user
