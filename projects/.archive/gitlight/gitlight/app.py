#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
GitLight Application
'''
# Python / Flask Imports
import flask
import flask_login

# GitLight Imports
from gitlight.libs import bootstrap


# Flask-Login requires the manager to be "global"
login_manager = flask_login.LoginManager()


def create_app(test_config=None):
    '''
    Initiate a front-end/user-facing instance of the GitLight application.
    '''
    app = flask.Flask(__name__, instance_relative_config=True)

    # Bootstrap configuration and routes
    bootstrap.load_configuration(app, test_config)
    bootstrap.load_routes(app)

    # Session management
    login_manager.init_app(app)
    login_manager.login_view = 'auth.user_login'

    return app
