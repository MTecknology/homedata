#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the wsgi mq transmitter
'''
# Python / Flask Imports
import pytest

# GitLight Imports
from gitlight.libs import utils
#from gitlight.libs.message_queue.xmit import wsgi as xmit


@pytest.mark.broken
def test_xmit(app):
    '''
    Test the wsgi transmitter.
    '''
    with app.test_request_context():
        return
        # TODO: Need to wrap gitlight.app in listener
        xm = xmit.xmit('wsgi:unix:/tmp/socket:/mq/ping', utils.encode({'action': 'ping'}))
        assert xm is not None
        assert utils.decode(xm) is not None
        assert 'pong' in utils.decode(xm)['body']

        xm = xmit.xmit('local:/foo', utils.encode({'action': 'ping'}))
        assert xm is not None
        assert utils.decode(xm) is not None
        assert 'invalid destination' in utils.decode(xm)['body']
