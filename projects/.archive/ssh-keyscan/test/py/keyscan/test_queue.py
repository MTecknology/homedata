#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Test Queue class in keyscan application
'''
# Python Ipmorts
import unittest.mock
import os
import tempfile

# Keyscan Imports
from keyscan import Queue

# Test Data
from test.py.data.queues import FILES, FILE_LINES


def test_is_automount():
    '''
    Test that is_automount() correctly determines if data is from an automount file.
    '''
    assert Queue.is_automount(FILE_LINES['automount']) == True
    assert Queue.is_automount(FILE_LINES['userlist']) == False
    assert Queue.is_automount([]) == None


def test_load_queue_without_ssh():
    '''
    Test that queue gets loaded correctly
    '''
    with unittest.mock.patch('socket.gethostname', return_value='svl-test'):
        q = Queue()
        tf = tempfile.mktemp()
        with open(tf, 'w') as fh:
            fh.write(FILES['userlist'])

        q.load_queue(tf, '/tmp')
        targets = q.get_targets('/scanhomes', False)

        assert type(targets) is list
        assert type(targets[0]) is tuple
        assert len(targets) == 4
        assert '.ssh' not in targets[0][1]

        os.remove(tf)


def test_load_queue_with_ssh():
    '''
    Test that queue gets loaded correctly
    '''
    with unittest.mock.patch('socket.gethostname', return_value='svl-test'):
        q = Queue()
        tf = tempfile.mktemp()
        with open(tf, 'w') as fh:
            fh.write(FILES['userlist'])

        q.load_queue(tf, '/tmp')
        targets = q.get_targets('/scanhomes', True)

        assert type(targets) is list
        assert type(targets[0]) is tuple
        assert len(targets) == 4
        assert '.ssh' in targets[0][1]

        os.remove(tf)


def test_build_input():
    '''
    Test that queue builds correct input from autofs file
    '''
    with unittest.mock.patch('socket.gethostname', return_value='svl-test'):
        q = Queue()
        tf_in = tempfile.mktemp()
        tf_out = tempfile.mktemp()
        with open(tf_in, 'w') as fh:
            fh.write(FILES['automount'])

        # Build targets
        q.build_input(tf_out, tf_in)

        q.load_queue(tf_out, '/tmp')
        targets = q.get_targets('/scanhomes', True)

        assert type(targets) is list
        assert type(targets[0]) is tuple
        assert len(targets) == 4
        assert '.ssh' in targets[0][1]

        os.remove(tf_in)
        os.remove(tf_out)
