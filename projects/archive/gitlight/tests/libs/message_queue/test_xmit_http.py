#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the http mq transmitter
'''
# Python / Flask Imports
import unittest

# GitLight Imports
from gitlight.libs import utils, message_queue

class MockResponse:
    '''
    Placeholder to mock response from requests library.
    '''
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_requests(*args, **kwargs):
    '''
    Function to highjack requests.post()
    '''
    resp = message_queue.receive(kwargs.get('json'))
    return MockResponse(resp, 200)


def test_xmit_success(app, agent):
    '''
    Test the http transmitter with a good option.
    '''
    with app.test_request_context():
        with unittest.mock.patch('requests.post', side_effect=mock_requests):
            # http
            xm = message_queue.send('http://127.0.0.1/mq', {'action': 'ping'})
            assert xm is not None
            assert xm['body'] == 'pong'

            # https
            xm = message_queue.send('https://127.0.0.1/mq', {'action': 'ping'})
            assert xm is not None
            assert xm['body'] == 'pong'


def test_xmit_error(app, agent):
    '''
    Test the http transmitter with a bad option.
    '''
    with app.test_request_context():
        with unittest.mock.patch('requests.post', side_effect=mock_requests):
            # http
            xm = message_queue.send('http://127.0.0.1/mq', {'action': 'surprise'})
            assert xm is not None
            assert xm['body'] == 'invalid option'

            # https
            xm = message_queue.send('https://127.0.0.1/mq', {'action': 'surprise'})
            assert xm is not None
            assert xm['body'] == 'invalid option'


def test_xmit_missing_action(app, agent):
    '''
    Test the http transmitter, with no action at all (and no dict).
    '''
    with app.test_request_context():
        with unittest.mock.patch('requests.post', side_effect=mock_requests):
            # https
            xm = message_queue.send('http://127.0.0.1/mq', 'surprise')
            assert xm is not None
            assert xm['body'] == 'action is required'

            # https
            xm = message_queue.send('https://127.0.0.1/mq', 'surprise')
            assert xm is not None
            assert xm['body'] == 'action is required'


def test_xmit_raise(app, agent):
    '''
    Test the http transmitter, raising an exception.
    '''
    with app.test_request_context():
        with unittest.mock.patch('requests.post', side_effect=KeyError('surprise')):
            # http
            xm = message_queue.send('http://127.0.0.1/mq', {'action': 'ping'})
            assert xm is not None
            assert xm['body'] == 'error transmitting data to destination'

            # https
            xm = message_queue.send('https://127.0.0.1/mq', {'action': 'ping'})
            assert xm is not None
            assert xm['body'] == 'error transmitting data to destination'
