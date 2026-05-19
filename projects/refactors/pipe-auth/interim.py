#!/usr/bin/env python3
'''
This script is used by the jabberd2-c2s process to verify user
credentials against the infrastructure application.

SIGUSR1 toggles logging level.
SIGUSR2 reloads configuration values.

Configuration:

  See the _defaults attribute of XmppConf() for available
  configuration settings and their default values.

  Files:
    /home/st/infrastructure/current/platforms/xmpp_constants.py
    /etc/jabberd2/xmpp_constants.py
'''

import base64
import collections
import hashlib
import importlib.util
import logging
import os
import pickle
import random
import re
import signal
import sys
import time
import urllib.request
import urllib.parse


class XmppConf(object):
    '''Parse configuration settings from various sources.'''
    _defaults = {
        # Start with debug logging and re-read config files with every
        # request to .get(). This re-checking stops once DEBUG_ENABLED
        # is set to False and requires a configuration reload (triggered
        # via SIGUSR2) to re-enable.
        'DEBUG_ENABLED': False,
        # Default cache lifetime: 1 wk
        'AUTHCACHE_TTL': 604800,
        # Whether to permit or verify all authentication attempts
        'AUTH_PERMIT_ALL': False,
        # Authentication provider (backend api host)
        'PIPEAUTH_HOST': '127.0.0.1',
        # Log file location; jabberd user must have write access
        'PIPEAUTH_LOGPATH': '/var/log/pipe-auth.log'}
    _attr = {}

    @classmethod
    def get(cls, key, default=None):
        '''Returns a config value if key is found or else returns None.'''
        if not cls._attr:
            cls.reload()
        elif cls._attr['DEBUG_ENABLED']:
            cls.reload()

        if key in list(cls._attr.keys()):
            return cls._attr[key]
        return default

    @classmethod
    def reload(cls):
        '''Load settings from files and merge the returned dictionaries.'''
        s_infra = cls._get_conf('/home/st/infrastructure/current/platforms/xmpp_constants.py')
        s_jabber = cls._get_conf('/etc/jabberd2/xmpp_constants.py')
        # s_infra supersedes s_jabber; s_jabber supersedes defaults
        cls._attr = {**cls._defaults, **s_jabber, **s_infra}

    @classmethod
    def _get_conf(cls, import_path):
        '''Returns a dictionary of parsed settings.'''
        if not os.path.isfile(import_path):
            return {}
        try:
            spec = importlib.util.spec_from_file_location('conf', import_path)
            conf = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(conf)
        except:
            logging.warning('Failed to load configuration from path: {}'.format(import_path))
            return {}
        return {x: getattr(conf, x, None) for x in dir(conf) if '__' not in x}

    @staticmethod
    def _get_api_host(*arg):  # pylint: disable=unused-argument
        '''PIPEAUTH_HOST should be moved from settings.py to xmpp_constants.py'''
        raise Exception('obsolete function: "settings.py" is no longer parsed.')


class AuthCache(object):
    '''A trivial object for storing cached credentials.'''
    User = collections.namedtuple('UserAuth', 'token_hash created_at')

    def __init__(self):
        self.enabled = True
        self.users = {}
        self.salt = random.random()

    def flush_cache(self):
        '''Flush data in cache.'''
        self.users = {}
        self.salt = random.random()

    def set_cache_enabled(self, enabled=True):
        '''Set cache to enabled or disabled state.'''
        self.enabled = enabled


class XmppAuth(object):
    '''Object to handle XMPP Authentication.'''
    def __init__(self):
        self.cache = AuthCache()
        # Supported domains and the API call to make
        self.api_calls = {
            'rpd.domain.tld': 'authenticate_device',
            'domain.tld': 'authenticate_user'}

        # Load up available commands; c2s cares about order
        self.cmd = collections.OrderedDict()
        self.cmd['OK'] = self._ok
        self.cmd['USER-EXISTS'] = self._user_exists
        self.cmd['CHECK-PASSWORD'] = self._check_password
        self.cmd['FREE'] = self._free

        self.auth_all = False
        self.refresh_authall()

    def refresh_authall(self):
        '''Refresh status of AUTH_ALL.'''
        # A sensu alert should exist that watches for the auth_all file.
        if self.auth_all != XmppConf.get('AUTH_PERMIT_ALL'):
            self.auth_all = not self.auth_all
            if self.auth_all:
                self.cmd['CHECK-PASSWORD'] = self._ok
            else:
                self.cmd['CHECK-PASSWORD'] = self._check_password

    def decode(self, s):
        '''Returns a string with unescaped chars for valid (& allowed) escapes.
        e.g. opscheck\40domain.tld --> 'opscheck@domain.tld'''
        out = s
        # Always replace the backslash last! This permits the allowed backslash
        # character while invalidating non-approved characters.
        replacements = (
            (r'\20', ' '),
            (r'\22', '"'),
            (r'\26', '&'),
            (r'\27', "'"),
            (r'\2f', '/'),
            (r'\3a', ':'),
            (r'\3c', '<'),
            (r'\3e', '>'),
            (r'\40', '@'),
            (r'\5c', '\\'))

        # For all allowed characters, replace the escaped version.
        for old, new in replacements:
            out = out.replace(old, new)

        return out

    def _user_exists(self, *args):
        '''Check if the username provided exists.'''
        # Not Implemented; always return success
        self._ok(args)

    def _check_password(self, args):
        '''Check password if correct arguments were passed.'''
        if len(args) != 3:
            return self._no()

        return self.check_password(self.decode(args[0]), args[1], args[2])

    def check_password(self, username, password, domain):
        '''Checks a user/password/domain against an API.'''
        time_now = int(time.time())

        logging.debug('Checking password for user "%s" in domain "%s".', username, domain)

        if domain not in list(self.api_calls.keys()):
            logging.warning('User: "%s" auth aganist invalid domain: "%s"', username, domain)
            return self._no()

        # Check if user has cached credentials; exit early if they match and return token
        cacheuser = '{}@{}'.format(username, domain)
        if self.cache.enabled and cacheuser in self.cache.users:
            if time_now > (self.cache.users[cacheuser].created_at + int(XmppConf.get('AUTHCACHE_TTL'))):
                logging.debug('Expiring cache for user: %s', username)
                del self.cache.users[cacheuser]
            elif self._gen_hash(password) == self.cache.users[cacheuser].token_hash:
                logging.debug('Valid cache for user: %s', username)
                if self.api_calls[domain] == 'authenticate_user':
                    return self._ok(password)
                return self._ok()

        # Build the opener object used for the API query
        url = 'http://{}:8080/api/1/{}/?format=pickle'.format(
            XmppConf.get('PIPEAUTH_HOST'), self.api_calls[domain])
        params = urllib.parse.urlencode({
            'username': username,
            'password': password,
            'domain': domain}).encode('utf-8')
        opener = urllib.request.build_opener()
        try:
            # Make sure string is correctly padded and make sure string is only ascii chars
            decoded = base64.b64decode(password + '=' * (-len(password) % 4)).decode('ascii')
            # If it looks like a session token was passed, set Cookie header.
            if re.match(r'^[a-z0-9]{32}$', decoded):
                logging.debug('Append Cookie header with sessionid.')
                opener.addheaders.append(('Cookie', 'sessionid={}'.format(decoded)))
        except:
            decoded = False

        try:
            # Query the API
            resp = opener.open(url, data=params).read()
            # Decode the API response
            token = pickle.loads(resp)
        except Exception as e:
            logging.exception('Error occured accessing api: %s', str(e))
            return self._no()

        # Check response; authentication succeeded if a "pickled" response was received.
        # Authentication fails if we could not read a token or if it was bool:False.
        if not token:
            logging.debug('Authentication failed.')
            return self._no()
        else:
            logging.debug('Authentication succeeded.')

        # Validate token and register user in cache
        if isinstance(token, bool):
            logging.debug('Valid response (True) received.')
            if self.cache.enabled:
                logging.debug('Register device in cache: %s', username)
                self.cache.users[cacheuser] = AuthCache.User(self._gen_hash(password), time_now)
                token = False  # RPD's do not use a token/cookie for authentication.
        elif isinstance(token, str):
            logging.debug('Valid response (token) received.')
            if re.match(r'^[a-z0-9]{32}$', token):
                if self.cache.enabled:
                    logging.debug('Register user in cache: %s', username)
                    self.cache.users[cacheuser] = AuthCache.User(self._gen_hash(token), time_now)
            else:
                logging.debug('Token is INVALID (format); removed.')
                token = False
        else:
            logging.debug('Token is INVALID (type:%s); removed.', str(type(token)))
            token = False

        # Return success
        if token:
            return self._ok(token)
        else:
            # Token was removed during validation
            return self._ok()

    def _gen_hash(self, val):
        '''Produce a hash from the input value combined with this session's salt.'''
        return hashlib.sha512((str(val) + str(self.cache.salt)).encode()).hexdigest()

    def _ok(self, token=''):
        '''Returns OK; appends session token if present.'''
        if token and isinstance(token, str):
            logging.debug('Returning OK <with token>')
            return 'OK {}'.format(token)
        else:
            logging.debug('Returning OK')
            return 'OK'

    def _no(self):
        '''Returns NO'''
        logging.debug('Returning NO')
        return 'NO'

    def _free(self, *args):  # pylint: disable=unused-argument
        '''Returns False.'''
        del args
        logging.debug('Returning False')
        return False


def main():
    '''Begin listening to stdin and processing requests.'''
    xa = XmppAuth()

    # Print available capabilities
    print((' '.join(list(xa.cmd.keys()))), flush=True)

    # Read lines from stdin and process one command per line
    logging.debug('Waiting for stdin...')
    for line in sys.stdin:
        args = line.split()
        if len(args) == 0:
            continue
        command = args.pop(0)

        # Make sure command is supported by our script
        if command not in list(xa.cmd.keys()):
            logging.warning('Unexpected command received: "%s"', command)
            continue

        # Run the requested command with supplied arguments
        logging.debug('Running command "%s"', command)
        if command == 'CHECK-PASSWORD':
            # Check to see if the auth_all file was created/deleted
            xa.refresh_authall()
        r = xa.cmd[command](args)
        if not r:
            continue

        # Finally, return a response
        print(r, flush=True)


def handle_signal(signum, *args):  # pylint: disable=unused-argument
    '''Generic interface to handle signals'''
    if signum == signal.SIGUSR1:
        logging.warning('SIGUSR1 received.')
        if logging.getLogger().getEffectiveLevel() == logging.WARNING:
            set_loglevel('DEBUG')
        else:
            set_loglevel('WARNING')
    elif signum == signal.SIGUSR2:
        logging.warning('SIGUSR2 received.')
        XmppConf.reload()
        if XmppConf.get('DEBUG_ENABLED'):
            set_loglevel('DEBUG')
        else:
            set_loglevel('WARNING')


def set_loglevel(level):
    '''Set the log level.'''
    lvl = getattr(logging, level, None)
    if not lvl:
        raise 'Invalid log level.'
    if logging.getLogger().getEffectiveLevel() != lvl:
        logging.warning('Setting log level to: {}'.format(level))
        logging.getLogger().setLevel(lvl)


if __name__ == '__main__':
    # Set up the log handler
    level = logging.WARNING
    if XmppConf.get('DEBUG_ENABLED'):
        level = logging.DEBUG
    logging.basicConfig(level=level, filename=XmppConf.get('PIPEAUTH_LOGPATH'))

    # Set up signal handling
    signal.signal(signal.SIGUSR1, handle_signal)
    signal.signal(signal.SIGUSR2, handle_signal)

    # Kick off main execution
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except:
        logging.exception('Exception running main():')
        raise
