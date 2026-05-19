#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test Fixtures: App
'''
# Python / Flask Imports
import pytest

# GitLight Imports
from gitlight.app import create_app


@pytest.fixture
def app():
    '''
    Create and configure a new app instance for each test.
    '''
    #db_fd, db_path = tempfile.mkstemp()

    instance = create_app({
        'TESTING': True,
        'MQ_SECRET': 'mock',
        'MQ_AGENT': 'local:',
        'LOG_LEVEL': 'CRITICAL',
        #'DATABASE': db_path,
    })

    # create the database and load test data
    #with instance.app_context():
    #    init_db()
    #    get_db().executescript(_data_sql)

    yield instance

    #os.close(db_fd)
    #os.unlink(db_path)


@pytest.fixture
def client(app):
    '''
    A test client for the app
    '''
    return app.test_client()
