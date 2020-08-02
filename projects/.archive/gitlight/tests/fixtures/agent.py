#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Text fixtures: Agent

This should only be used for testing functions that can not be tested from /mq
tests, similar to routes/frontpage.test_ping().
'''
# Python / Flask Imports
import pytest

# GitLight Imports
from gitlight.agent import create_agent


@pytest.fixture
def agent():
    '''
    Create and configure a new agent instance for each test.
    '''
    # create the instance with common test config
    instance = create_agent({
        'TESTING': True,
        'MQ_SECRET': 'mock',
        'MQ_AGENT': 'local:',
        #'DATABASE': db_path,
    })  

    yield instance
