#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Message Queue
=============

Library for talking to other gitlight services.
'''
# Python / Flask Imports
import flask
import importlib

# GitLight Imports
from gitlight.libs import utils

ERROR_TEMPLATE = {
    'message': {
        'success': False,
        'body': '',
    }
}


def send(destination, message):
    '''
    Send a message to a gitlight agent.

    Returns dict():
        - reply_to    ID of message being replied to
        - success     True='success', False='failure', None='xmit error'
        - body        Typical location for response "message/content"
        - ???         Any additional response data

    :param destination:
        Host to receive data

    :param message:
        Python dictionay to be sent.

        - message_id   Optional ID used to verify receipt of the correct response
        - action       Operation being requested from endpoint (see message_queue.api)
        - ???          Any additional information being sent to 'action' endpoint

    **Example:**

        send('wsgi:/run/gitlight-agent.socket', {
            'message_id': libs.utils.uuid(5),
            'action': 'ping',
            'garbage': 'this is unused/discarded',
            })
    '''
    ret = {}
    err = ERROR_TEMPLATE
    if 'action' not in message:
        err['body'] = 'action is required'
        return err

    if ':' not in destination:
        destination = '{}{}'.format(flask.current_app.config['MQ_AGENT'], destination)

    msg_pk = {'message_pack': utils.encode(message)}
    try:
        proto = destination.split(':')[0]
        mod = importlib.import_module('gitlight.libs.message_queue.xmit.{}'.format(proto))
    except ModuleNotFoundError:
        mod = importlib.import_module('gitlight.libs.message_queue.xmit.invalid')

    xmit = mod.xmit(destination, msg_pk)
    return utils.decode(xmit['message_pack'])


def receive(msg_pk):
    '''
    Respond to a message delivered by gitlight service.

    Returns a python dictionary, see ``send()`` for details.
    '''
    err = {'reply_to': None, 'success': False, 'body': None}
    message = utils.decode(msg_pk['message_pack'])

    if not message:
        err['body'] = 'validation failure'
    elif type(message) is not dict:
        err['body'] = 'malformed message'
    elif 'action' not in message:
        err['body'] = 'message[action] is required'
        err['reply_to'] = message.get('message_id')
    if err['body'] is not None:
        return {'message_pack': utils.encode(err)}

    # operations are expected to return a dict: {'success': T|F|N, body: '', ...}
    try:
        mod = importlib.import_module('gitlight.api.{}'.format(message['action']))
    except:
        mod = importlib.import_module('gitlight.api.invalid')

    response = mod.action(message)
    response['reply_to'] = message.get('message_id')
    return {'message_pack': utils.encode(response)}
