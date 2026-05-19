#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
WSGI
====

Message Queue handler for WSGI transmit destinations.
'''


def xmit(destination, message):
    '''
    Handle transmit via wsgi.
    '''
    return {'success': False, 'body': 'transmit method not implemented'}
