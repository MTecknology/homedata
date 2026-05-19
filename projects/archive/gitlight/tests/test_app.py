#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test application loading and critical components
'''
# GitLight Imports
from gitlight.app import create_app

def test_config():
    '''
    Test app creation with/without test config.
    '''
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
