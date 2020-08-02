#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Test the test library.
'''
# Python Imports
import pytest
import timeit

# GitLight Imports
from gitlight.libs import test


def test_echo():
    '''
    Test echo function.
    '''
    # Response is unchanged
    assert test.echo('foo') == 'foo'


@pytest.mark.slow
def test_sleep():
    '''
    Test sleep function.
    '''
    # Require valid input
    assert test.sleep(-1) == False

    # Function returns True
    start = timeit.default_timer()
    assert test.sleep(3) == True
    tik = (timeit.default_timer() - start)

    # Took longer than 1 second
    assert tik > 1

    # Took less than 5 seconds
    assert tik < 5


@pytest.mark.slow
def test_sleep_r():
    '''
    Test sleep_r function.
    '''
    # Require valid input
    assert test.sleep_r(-1) == False

    # Function returns True
    start = timeit.default_timer()
    assert test.sleep_r(3) == True
    tik = (timeit.default_timer() - start)

    # Took time to return
    assert tik > 0

    # Took less than 5 seconds
    assert tik < 5
