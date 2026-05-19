#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test agent loading and critical components
'''
# GitLight Imports
from gitlight.agent import create_agent

def test_config():
    '''
    Test agent creation with/without test config.
    '''
    assert not create_agent().testing
    assert create_agent({'TESTING': True}).testing
