#!/usr/bin/env python2
'''
This script deletes rows from a mysql db/table (diagnostics.diagnostics_historydump)
that have been marked as being processed by other services.

SIGUSR1 toggles logging level.
SIGUSR2 reloads configuration values.

Configuration:

  See the _defaults attribute of DiagConf() for available
  configuration settings and their default values.

  Files:
    /root/.diag_cleanup.py
    /etc/.diag_cleanup.py
'''

import json
import logging
import MySQLdb
import os
import signal
import sys
import time


class DiagConf(object):
    '''Parse configuration settings from various sources.'''
    _defaults = {
        # Start with debug logging and re-read config files with every
        # request to .get(). This re-checking stops once DEBUG_ENABLED
        # is set to False and requires a configuration reload (triggered
        # via SIGUSR2) to re-enable.
        'DEBUG_ENABLED': False,
        # Log file location
        'LOG_PATH': '/var/log/diag_cleanup.log',
        # Location of dump files
        'DUMP_DIR': os.path.expanduser('~st/infrastructure/uploaded_files/dumps/'),
        # Database credentials
        'DB_USER': '',
        'DB_PASS': '',
        'DB_HOST': '127.0.0.1',
        'DB_NAME': 'diagnostics',
        'DB_TABLE': 'diagnostics_historydump',
        # Optimizations
        'QUERY_LIMIT': 10000,
        'SLEEP_TIME': 10}
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
        conf = {}
        conf.update(cls._defaults)
        conf.update(cls._get_conf('/etc/.diag_cleanup.json'))
        conf.update(cls._get_conf('/root/.diag_cleanup.json'))
        cls._attr = conf

    @classmethod
    def _get_conf(cls, import_path):
        '''Returns a dictionary of parsed settings.'''
        if not os.path.isfile(import_path):
            return {}
        try:
            with open(import_path, 'r') as fh:
                return json.load(fh)
        except:
            logging.warning('Failed to load configuration from path: {}'.format(import_path))
        return {}


class DiagCleanup(object):
    '''Object to handle Diagnostics Cleanup.'''
    def __init__(self):
        self.db = self._get_db()

    def _get_db(self):
        logging.info('Establishing database connection.')
        return MySQLdb.connect(
            DiagConf.get('DB_HOST'),
            DiagConf.get('DB_USER'),
            DiagConf.get('DB_PASS'),
            DiagConf.get('DB_NAME'))

    def run(self):
        cursor = self.db.cursor()
        rm_rows = []

        rows = self.get_rows(cursor)
        if not rows:
            logging.debug('Early return from processing: no diagnostic rows found.')
            return None

        # For each processed dump, collect a row ID and delete the file
        for row in rows:
            rm_rows.append(row[0])
            self.delete_file(row[1])
        # Delete rows of processed files
        self.delete_rows(cursor, rm_rows)

        # Release cursor
        cursor.close()


    def get_rows(self, cursor):
        '''Returns a list of processed dumps in the form of tuple(id, dump).'''
        logging.debug('Collecting completed diagnostics rows.')
        cursor.execute(
                'SELECT id, dump FROM {}.{} '
                'WHERE network_diagnostics_processed="p" '
                'AND refactoring_processed="p" '
                'AND sentry_reports_processed="p" '
                'ORDER BY id ASC LIMIT {}'.format(
                    DiagConf.get('DB_NAME'),
                    DiagConf.get('DB_TABLE'),
                    DiagConf.get('QUERY_LIMIT')))

        ret = cursor.fetchall()
        if not ret:
            return []
        return ret

    def delete_rows(self, cursor, rows):
        row_ids = ', '.join(map(str, rows))
        logging.debug('Removing diagnostics rows.'.format(row_ids))
        cursor.execute(
                'DELETE FROM {}.{} '
                'WHERE id IN ({})'.format(
                    DiagConf.get('DB_NAME'),
                    DiagConf.get('DB_TABLE'),
                    row_ids))
        self.db.commit()

    def delete_file(self, filename):
        fpath = filename.replace('dumps/', DiagConf.get('DUMP_DIR'))
        try:
            os.remove(fpath)
        except:
            logging.warning('Unable to delete file: {}'.format(fpath))


def main():
    '''Launch into an infinite loop: run cleanup, sleep, repeat.'''
    DiagConf.reload()
    dc = DiagCleanup()

    while True:
        logging.debug('Running diag cleanup.')
        dc.run()
        logging.debug('Sleeping before next execution.')
        time.sleep(DiagConf.get('SLEEP_TIME'))


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
        DiagConf.reload()
        if DiagConf.get('DEBUG_ENABLED'):
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
    if DiagConf.get('DEBUG_ENABLED'):
        level = logging.DEBUG
    logging.basicConfig(level=level, filename=DiagConf.get('LOG_PATH'))

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
