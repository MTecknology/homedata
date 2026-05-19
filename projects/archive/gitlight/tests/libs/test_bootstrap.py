#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the bootstrap library.
'''
# Python / Flask Imports
import six
import unittest.mock

# GitLight Imports
from gitlight.libs import bootstrap
from gitlight.app import create_app


def test_load_configuration():
    '''
    Test configuration loading
    '''
    app = create_app()
    assert bootstrap.load_configuration(app) is None


def test_load_routes():
    '''
    Test routes loading
    '''
    app = create_app()
    assert bootstrap.load_routes(app) is None
    assert bootstrap.load_routes(app, '/invalid') == False


def test_load_route():
    '''
    Test routes loading
    '''
    app = create_app()
    assert bootstrap.load_route(app, 'frontpage') is None
    assert bootstrap.load_route(app, 'in_val_id') == False


@unittest.mock.patch('importlib.import_module', return_value=six)
def test_bad_route(self):
    '''
    Test loading route with no blueprint
    '''
    app = create_app()
    assert bootstrap.load_route(app, 'dummy') is False
