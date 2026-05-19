#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
MQ Op: Ping
===========

Message Queue handler for ping requests.
'''


def action(message):
    '''
    Return pong to ping request.
    '''
    return {'success': True, 'body': 'pong'}
