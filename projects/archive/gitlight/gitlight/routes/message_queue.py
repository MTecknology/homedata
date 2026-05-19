#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Routes used for messaging between gitlight services.
'''
# Python / Flask Imports
import flask

# GitLight Imports
import gitlight.libs.message_queue as message_queue
import gitlight.libs.utils as utils

# Blueprint: frontpage
bp = flask.Blueprint('message_queue', __name__)


@bp.route('/mq', methods=['POST'])
def mq_message():
    '''
    Handle a Message_Queue request.

    | Path: /mq
    | Methods: POST
    '''
    if not flask.request.content_type == 'application/json':
        return flask.jsonify({'message_pack': utils.encode({
            'success': False,
            'body': 'incorrect content-type'})})
    msg_pk = flask.request.get_json()

    response = message_queue.receive(msg_pk)
    return flask.jsonify(response)


@bp.route('/mq/ping', methods=['GET'])
def mq_ping():
    '''
    Ping backend services and return the response.

    | Path: /mq/ping
    | Methods: GET
    '''
    message = {'message_id': utils.uuid(5), 'action': 'ping'}
    response = message_queue.send('/mq', message)
    return 'Ping ID: {}<br>Response: {}'.format(message['message_id'], response)
