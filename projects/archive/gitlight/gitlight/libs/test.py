#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Library for running arbitrary tests.
'''
import random
import time


def echo(text):
    '''
    Return a string of text.

    :param text:
        String of text to be returned.

    .. code-block:: python

        test.echo('red rum')
    '''
    return text


def sleep(seconds):
    '''
    Pause execution and return True.

    :param seconds:
        Number of seconds to sleep before returning.

    .. code-block:: python

        test.sleep(60)
    '''
    if int(seconds) <= 0:
        return False
    time.sleep(int(seconds))
    return True


def sleep_r(seconds=60):
    '''
    Pause execution for a random period of time and return True.

    :param seconds:
        Maximum number of seconds to sleep before returning.

    .. code-block:: python

        test.sleep_r(180)
    '''
    if int(seconds) <= 0:
        return False
    time.sleep(random.randint(1, seconds))
    return True
