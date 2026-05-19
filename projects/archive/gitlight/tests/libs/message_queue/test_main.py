#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the message_queue; library.
'''
# GitLight Imports
from gitlight.libs import message_queue as mq, utils


def test_send(app):
    '''
    Test MQ Send
    '''
    with app.test_request_context():
        assert mq.send('local:/mq/ping', {'message_id': '123'})['body'] == 'action is required'
        assert 'pong' in mq.send('local:/mq/ping', {'action': 'ping'})['body']
        assert 'invalid option' in mq.send('local:/mq/ping', {'action': 'does_not_exist'})['body']
        assert 'invalid destination prefix' in mq.send('redrum:', {'action': 'ping'})['body']


def test_receive(app):
    '''
    Test MQ Receive
    '''
    with app.test_request_context():
        uid = utils.uuid(7)
        assert utils.decode(mq.receive({'message_pack': utils.encode({
            'message_id': uid,
            'action': 'ping'})})['message_pack'])['body'] == 'pong'
        assert 'is required' in utils.decode(mq.receive({'message_pack': utils.encode({
            'message_id': uid})})['message_pack'])['body']
        assert 'invalid option' in utils.decode(mq.receive({'message_pack': utils.encode({
            'message_id': uid,
            'action': 'does_not_exist'})})['message_pack'])['body']
        assert 'invalid option' in utils.decode(mq.receive({'message_pack': utils.encode({
            'message_id': uid,
            'action': 'does-not-exist'})})['message_pack'])['body']
        assert 'malformed message' in utils.decode(mq.receive({
            'message_pack': utils.encode('jargon')})['message_pack'])['body']
        assert 'validation failure' in utils.decode(mq.receive({'message_pack': {
            'message_id': uid,
            'action': 'ping'}})['message_pack'])['body']
