#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the local mq transmitter
'''
# GitLight Imports
from gitlight.libs import utils
from gitlight.libs.message_queue.xmit import local as xmit


def test_xmit(app):
    '''
    Test the local transmitter.
    '''
    with app.test_request_context():
        xm = xmit.xmit('local:/mq/ping', {'message_pack': utils.encode({'action': 'ping'})})
        assert xm is not None
        assert utils.decode(xm['message_pack']) is not None
        assert 'pong' in utils.decode(xm['message_pack'])['body']

        xm = xmit.xmit('local:/foo', {'message_pack': utils.encode({'action': 'ping'})})
        assert xm is not None
        assert utils.decode(xm['message_pack']) is not None
        assert 'invalid destination' in utils.decode(xm['message_pack'])['body']
