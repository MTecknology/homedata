#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test message_queue routes
'''
# Python / Flask Imports
import json

# GitLight Imports
import gitlight.libs.utils as utils


def test_ping(agent):
    '''
    Test that a ping returns.
    '''
    with agent.test_client() as client:
        response = client.get('/mq/ping')
        assert b'pong' in response.data


def test_message(agent):
    '''
    Test message queue handling.
    Note: This is for the handler, not anything more (no action/ops).
    '''
    with agent.test_request_context():
        with agent.test_client() as client:
            uid = utils.uuid(7)

            # valid
            response = client.post('/mq',
                    content_type='application/json',
                    json={
                        'message_pack': utils.encode({
                            'message_id': uid,
                            'action': 'ping',
                        })},
                    )
            assert 'pong' in utils.decode(response.json['message_pack'])['body']

            # valid / unsigned
            response = client.post('/mq',
                    content_type='application/json',
                    json={
                        'message_pack': {
                            'message_id': uid,
                            'action': 'ping',
                            }},
                    )
            assert 'validation failure' in utils.decode(response.json['message_pack'])['body']

            # invalid option
            response = client.post('/mq',
                    content_type='application/json',
                    json={
                        'message_pack': utils.encode({
	                        'action': 'does_not_exist',
        	                })},
                    )
            assert 'invalid option' in utils.decode(response.json['message_pack'])['body']

            # invalid action name (hyphen in mod name)
            response = client.post('/mq',
                    content_type='application/json',
                    json={
                        'message_pack': utils.encode({
	                        'message_id': uid,
        	                'action': 'does-not-exist',
                	        })},
                    )
            assert 'invalid option' in utils.decode(response.json['message_pack'])['body']

            # invalid content-type
            response = client.post('/mq',
                    data={
                        'message_pack': utils.encode({
	                        'message_id': uid,
        	                'action': 'ping',
                	        })},
                    )
            assert 'incorrect content-type' in utils.decode(response.json['message_pack'])['body']
