#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
MQ Op: Access Check
===================

Message Queue handler for check_access requests.
'''


def action(message):
    '''
    Return True if user has access to resource
    '''
    uname = message.get('username', None)
    path = message.get('path', None)
    if not uname or not path:
        return {'success': False, 'body': 'no username|path provided'}
    #TODO
    return {'success': False, 'body': 'not implemented'}
