#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Library of miscellaneous utility functions.
'''
# Python / Flask Imports
import base64
import hashlib
import itsdangerous
import six
import urllib.parse

from flask import current_app, request, url_for
from uuid import uuid4


def decode(message):
    ''' 
    Decode a message, using MQ_SECRET, into a python object.

    :param message:
        python object to be encoded
    '''
    s = itsdangerous.JSONWebSignatureSerializer(current_app.config['MQ_SECRET'])
    try:
        return s.loads(base64.b64decode(bytes(message, 'ascii')))
    except:
        return None


def encode(message):
    ''' 
    Encode a python object, using MQ_SECRET, for transmitting.

    :param message:
        python object to be encoded
    '''
    s = itsdangerous.JSONWebSignatureSerializer(current_app.config['MQ_SECRET'])
    return base64.b64encode(s.dumps(message)).decode('ascii')


def uuid(length=32):
    '''
    Return a somewhat-random string.

    :param length:
        length of string returned (max: 32)
    '''
    return uuid4().hex.upper()[0:length]


def hash(text):
    '''
    Return a hash value for supplied text.

    :param text:
        Any text to be hashed.
    '''
    return hashlib.sha512(text.encode()).hexdigest()

def is_safe_url(target):
    '''
    Ensure a redirect will return to the same server. Returns boolean; True if safe.

    :param target:
        Requested target URL
    '''
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
