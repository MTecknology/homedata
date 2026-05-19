#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
HTTPS
=====

Message Queue handler for HTTPS transmit destinations.
'''
from gitlight.libs.message_queue.xmit import http


def xmit(destination, message):
    '''
    Handle transmit via https.
    '''
    return http.xmit(destination, message)
