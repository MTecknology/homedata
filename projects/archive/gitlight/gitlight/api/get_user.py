#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
MQ Op: Get User
===============

Message Queue handler for get_user requests.
'''
# Python / Flask Imports
import six
import yaml

# GitLight Imports
from gitlight.libs import git


def action(message):
    '''
    Return user data (profile, gpg keys, password hashes, etc.).
    '''
    if not isinstance(message, dict):
        return {'success': False, 'body': 'bad message data'}

    username = message.get('username', None)
    if not username:
        return {'success': False, 'body': 'no username provided'}

    udata = git.read_file('gitolite-admin.git', 'HEAD', 'users/{}/data.yml'.format(username))
    if not udata:
        return {'success': False, 'body': 'error loading data'}

    try:
        user = yaml.safe_load(udata)
    except:
        return {'success': False, 'body': 'error parsing data'}
    if not isinstance(user, dict):
        return {'success': False, 'body': 'error parsing data'}

    # Repair potential mistakes and massage data
    user['username'] = username
    if isinstance(user.get('passwords', []), six.string_types):
        user['passwords'] = [user['passwords']]
    if 'password' in user:
        if not 'passwords' in user:
            if isinstance(user['password'], six.string_types):
                user['passwords'] = [user['password']]
            elif isinstance(user['password'], list):
                user['passwords'] = user['password']
        del user['password']
    user['gecos_fields'] = {k.replace('gecos_', ''): v for (k, v) in user.items() if k.startswith('gecos_')}

    return {'success': True, 'body': user}
