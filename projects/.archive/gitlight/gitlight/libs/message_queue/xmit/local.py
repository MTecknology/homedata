#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Local
=====

Message Queue handler for handling local requests.

This is useful for local testing and running a stand-alone instance.
'''
# Python / Flask Imports
import flask

# GitLight Imports
from gitlight.libs import message_queue as mq, utils


def xmit(destination, message):
    '''
    Handle direct transmitions.
    '''
    err = mq.ERROR_TEMPLATE
    if not destination.startswith('local:/mq'):
        err['body'] = 'invalid destination'
        return {'message_pack': utils.encode(err)}
    return mq.receive(message)
