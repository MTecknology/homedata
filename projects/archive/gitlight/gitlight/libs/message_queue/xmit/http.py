#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
HTTP
====

Message Queue handler for HTTP transmit destinations.
'''
# Python / Flask Imports
import requests

# GitLight Imports
import gitlight.libs.message_queue as message_queue
from gitlight.libs import utils


def xmit(destination, message):
    '''
    Handle transmit via http(s).
    '''
    err = message_queue.ERROR_TEMPLATE
    try:
        response = requests.post(
                url=destination,
                headers={'content-type': 'application/json'},
                json=message)
    except Exception as e:
        err['body'] = 'error transmitting data to destination'
        return {'message_pack': utils.encode(err)}

    return response.json()
