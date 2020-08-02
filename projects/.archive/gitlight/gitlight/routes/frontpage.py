#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Basic route for handling the front page.
'''
# Python / Flask Imports
import flask

# GitLight Imports
import gitlight.routes.message_queue as mq_routes

# Blueprint: frontpage
bp = flask.Blueprint('frontpage', __name__)


@bp.route('/', methods=['GET', 'HEAD'])
def index():
    '''
    Return a pretty rendering of the front page.

    | Path: /
    | Methods: GET, HEAD
    '''
    return flask.render_template('gitlight/frontpage_index.html')


@bp.route('/ping', methods=['GET'])
def ping():
    '''
    Stub function to include restricted route message_queue.ping().

    | Path: /ping
    | Methods: GET
    '''
    return mq_routes.mq_ping()
