#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
MQ Op: Invalid
==============

Message Queue handler for invalid requests.
'''


def action(message):
    '''
    Handle invalid option targets.
    '''
    return {'success': False, 'body': 'invalid option'}
