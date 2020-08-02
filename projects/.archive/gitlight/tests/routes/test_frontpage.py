#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test frontpage routes
'''


def test_index(client):
    '''
    Test that the homepage renders.
    '''
    response = client.get('/')
    assert b'GitLight' in response.data


def test_ping(client):
    '''
    Test the ping handler.
    '''
    response = client.get('/ping')
    assert b'pong' in response.data
