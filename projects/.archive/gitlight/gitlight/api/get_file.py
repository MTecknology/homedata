#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
MQ Op: Get File
===============

Message Queue handler for get_file requests.
'''


def action(message):
    '''
    Return contents of requested file.
    '''
    fname = message.get('filename', None)
    if not fname:
        return {'success': False, 'body': 'no filename provided'}
    #TODO
    return {'success': False, 'body': 'not implemented'}
