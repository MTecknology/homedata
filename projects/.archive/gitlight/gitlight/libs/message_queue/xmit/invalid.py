#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Invalid
=======

Message Queue handler for invalid transmit destinations.
'''
# GitLight Imports
from gitlight.libs import utils


def xmit(destination, message):
    '''
    Handle invalid transmit methods.
    '''
    return {'message_pack': utils.encode({'success': False, 'body': 'invalid destination prefix'})}
