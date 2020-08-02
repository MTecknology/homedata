#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Routes for handling authentication requests.
'''
# Python / Flask Imports
import flask
import flask_login
import functools

# GitLight Imports
import gitlight.mods.auth as auth
from gitlight.app import login_manager
from gitlight.libs import utils


# Blueprint: auth
bp = flask.Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(username):
    '''
    Retreive user data for current session
    '''
    return auth.get_user(username, False)


@bp.route('/login', methods=['GET', 'POST'])
def user_login():
    '''
    Return a basic login page.

    | Path: /login
    | Methods: GET, POST
    '''
    if flask.request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return flask.redirect('/user/{}'.format(flask_login.current_user.id))
        return flask.render_template('gitlight/auth_login.html')

    username = flask.request.form.get('user', None)
    password = utils.hash(flask.request.form.get('pass', ''))
    remember = flask.request.form.get('memberberries', False)
    forward = flask.request.args.get('next')

    user = auth.get_user(username, True)
    if not user:
        return flask.render_template('gitlight/auth_login.html', errors=['Authentication Failed'])

    if password not in user.passwords:
        return flask.render_template('gitlight/auth_login.html', errors=['Authentication Failed'])

    flask_login.login_user(user, remember)

    if not utils.is_safe_url(forward):
        return flask.abort(400)
    return flask.redirect(forward or '/user/{}'.format(user.id))


@bp.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logout():
    '''
    Remove stored session.

    | Path: /logout
    | Methods: GET
    '''
    flask_login.logout_user()
    return flask.redirect(flask.url_for('frontpage.index'))


@bp.route('/user/<username>', methods=['GET'])
def show_user(username):
    '''
    Show a basic profile page for a user.

    | Path: /user/<username>
    | Methods: GET
    '''
    user = auth.get_user(username, False)
    if not user:
        return flask.render_template('gitlight/error.html', error='Profile not found')
    return flask.render_template('gitlight/auth_user.html', userdata=user)
