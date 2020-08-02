#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Library for bootstrapping GitLight instances.
'''
# Python / Flask Imports
import importlib
import logging
import os


def load_configuration(app, test_config=None):
    '''
    Load configuration into a supplied gitlight application.

    :param app:
        Flask application configuration is being loaded for.

    :param test_config:
        Dictionary of extra configuration options, used for teting.

    **Configuration Options:**

    .. code:: text

        G3_ROOT (default: '/var/lib/gitolite3')
            Gitolite3 root directory.

        LOG_PATH (default: None)
            File path to log messages to. Default: None (stdout)

        LOG_LEVEL (default: WARNING)
            Application logging level. Uses python ``logging`` levels.

        MQ_AGENT (default: None, required)
            Agent handling gitolite3 requests. (ex. https://git.domain.tld)
            Supported protocols: [https, http, unix]

        MQ_SECRET (default: '')
            Key used for cryptographic verification of communication (message_queue).

        SECRET_KEY (default: '', required)
            Key used for flask secrets, such as session storage.

        SESSION_PROTECTION (default: 'strong', required)
            Level of protection to use for session storage.
            Supported levels: [None, 'basic', 'strong']
    '''
    app.config.from_mapping(
        G3_ROOT='/var/lib/gitolite3',
        LOG_PATH=None,
        LOG_LEVEL='WARNING',
        MQ_AGENT=None,
        MQ_SECRET='insecure',
        SECRET_KEY='insecure',
        SESSION_PROTECTION='strong',
    )

    # Find possible configuration locations, use first found
    if os.path.isfile('config.py') or os.path.isfile('../config.py'):
        app.config.from_pyfile('config.py', silent=True)
        app.config.from_pyfile('../config.py', silent=True)
    elif os.path.isfile('/etc/gitlight/config.py'):
        app.config.from_pyfile('/etc/gitlight/config.py')

    # Load the test config, if provided
    if test_config:
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configure log level
    logging.getLogger('werkzeug').setLevel(app.config['LOG_LEVEL'])


def load_routes(app, basepath=None):
    '''
    Load routes (blueprints) from an application path into a supplied gitlight application.

    :param app:
        Flask application configuration is being loaded for.

    :param basepath:
        Root location of GitLight application.

    .. code-block:: python

        app = flask.Flask()
        bootstrap.load_routes(app)
    '''
    if not basepath:
        basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.logger.debug('Loading routes from: {}'.format(basepath))

    if not os.access(basepath, os.R_OK):
        app.logger.error('Unable to read from application source.')
        return False

    for fname in os.listdir('{}/routes/'.format(basepath)):
        route, sfx = fname[:-3], fname[-3:]

        if fname == '__init__.py' or sfx != '.py':
            continue
        # Restricted Routes
        if fname in ['message_queue.py']:
            continue

        load_route(app, route)


def load_route(app, route):
    '''
    Load a single route (blueprints) into a supplied gitlight application.

    :param app:
        Flask application configuration is being loaded for.

    :param route:
        Load routes from named python file.

    .. code-block:: python

        app = flask.Flask()
        bootstrap.load_routes(app, 'frontpage')
    '''
    app.logger.debug('Loading routes for: {}'.format(route))
    try:
        blueprint = importlib.import_module('gitlight.routes.{}'.format(route))
    except ModuleNotFoundError as e:
        app.logger.warning('Failed to load routes for: {}'.format(route))
        app.logger.warning('Error: {}'.format(e))
        return False

    if not hasattr(blueprint, 'bp'):
        app.logger.warning('No blueprint found in route: {}'.format(route))
        return False

    bp = getattr(blueprint, 'bp')
    app.register_blueprint(bp)
