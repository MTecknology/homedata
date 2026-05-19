#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
GitLight Application
'''
# Python / Flask Imports
import flask

# GitLight Imports
from gitlight.libs import bootstrap


def create_agent(test_config=None):
    '''
    Initiate a gitlight-to-gitolite3 gateway agent.
    '''
    agent = flask.Flask(__name__, instance_relative_config=True)
    bootstrap.load_configuration(agent, test_config)
    bootstrap.load_route(agent, 'message_queue')
    return agent
