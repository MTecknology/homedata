#!/usr/bin/env python
'''
Scan directories for unencrypted ssh keys and optionally delete them.

Author: Michael Lustfield
Copyright: Juniper Networks
License: GPLv3+
'''
import argparse
import datetime
import logging
import multiprocessing
import os
import random
import shutil
import subprocess
import socket
import stat
import sys
import tempfile

import six
import yaml

from lib.timeout import timeout, TimedOutError
from lib.lockfile import LockFile
from lib.uploader import compile_results, sp_upload


class Queue(object):
    '''Object used to maintain a queue of directories to scan'''

    def __init__(self):
        self._incomplete = list()

    def get_targets(self, prefix, append_ssh=False):
        '''Return a list of targets to scan'''
        if not self._incomplete:
            raise Exception('No target available')
        if prefix[-1:] != '/':
            prefix += '/'
        ssh = '/.ssh' if append_ssh else ''
        return [(x, prefix + x + ssh) for x in self._incomplete]

    def load_queue(self, path, completed_dir):
        '''Build work queue from file path, excluding completed'''
        with open(path, 'r') as fh:
            incomplete = set([x.replace('\n', '')
                              for x in fh.readlines()
                              if len(x.strip()) > 0])

        try:
            completed = set(os.listdir(completed_dir))
        except OSError:
            completed = []

        LOGGER.debug('Skipping completed scans: %s', completed)

        self._incomplete = list(incomplete.difference(completed))
        random.shuffle(self._incomplete)

    def build_input(self, path, autofs):
        '''Build input file from autofs file'''
        # This assumes the format <geo>-scanner.domain.tld
        local_geo = socket.gethostname().split('-')[0]
        known_geos = {
            'dc1': 'dc1',
            'dc2': 'dc2',
            'dc3': 'dc3',
            'dc4': 'dc4',
            ##
            'wf': 'dc4',
            'maniac1': 'dc4',
            'baas_dc2_users_in_dc3': 'dc3',
            'baas_dc3_users_in_dc2': 'dc2',
            'localhost': None,  # invalid
            }

        if local_geo not in ['dc1', 'dc2', 'dc3', 'dc4']:
            raise Exception('Could not determine geo of this host')

        with open(autofs, 'r') as _in:
            lines = [line for line in _in.readlines() if
                     not line.startswith('#') and
                     len(line.strip()) > 0]

        if not self.is_automount(lines):
            raise Exception(
                'Provided afs file does not appear to be autofs format.')

        valid_mounts = self.find_accessible_mounts(lines)

        excluded = {'wrong_geo': [], 'broken_geo': [], 'bad_mount': []}
        with open(path, 'w') as _out:
            for line in lines:
                user = line.split()[0].strip()
                mount_path = line.split()[1].strip()
                nfs_root = mount_path[0:mount_path.rindex('/')]
                nfs_geo = mount_path.split(':')[0].split('-')[0]
                mapped_geo = known_geos.get(nfs_geo, nfs_geo)

                if mapped_geo is None:
                    # Skip hosts known to be broken
                    excluded['broken_geo'].append(user)
                    continue

                if nfs_root not in valid_mounts:
                    # Skip users with an inaccessible nfs host
                    excluded['bad_mount'].append(user)
                    continue

                if mapped_geo in known_geos and mapped_geo != local_geo:
                    # Skip if geo is known and does not match local_geo
                    # Scanning should be performed on a local server
                    excluded['wrong_geo'].append(user)
                    continue

                _out.write('{}\n'.format(user))

            for reason, users in excluded.items():
                LOGGER.warning('Skipping users (reason: %s; count: %s): %s',
                               reason, str(len(users)), users)

    @staticmethod
    def find_accessible_mounts(lines):
        '''Returns a list of mounts that are accessible to this host'''
        # Find mount points from autofs list
        mounts = []
        for line in lines:
            mount_path = line.split()[-1]
            nfs_root = mount_path[0:mount_path.rindex('/')]
            if nfs_root not in mounts:
                mounts.append(nfs_root)

        # Remove unmountable mount points
        test_path = tempfile.mkdtemp()
        for mount in mounts:
            process = subprocess.Popen(
                ['mount', mount, test_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr or process.returncode:
                # Remove mount if it could not be mounted
                mounts.remove(mount)
            # Ensure path is unmounted
            _ = subprocess.Popen(
                ['umount', test_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).wait()
        shutil.rmtree(test_path)

        return mounts

    @staticmethod
    def is_automount(lines):
        '''Returns True if path is an automount file; None if error'''
        if not lines:
            return None
        # Process lines bottom-up
        for i in range(len(lines)):
            line = lines[(i + 1) * -1]
            # Stop if line is not blank
            if len(line.strip()) > 0:
                break
            # Return error state if all lines are blank
            if i == len(lines):
                return None
        if any(c.isspace() for c in line):
            return True
        return False


class OptsParser(object):
    '''Object for handling arguments passed to script'''

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            usage='scandir [-h] <optional arguments>',
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog,
                width=100))
        self._add_opts()

    def parse_opts(self):
        '''Return parsed options'''
        return self.parser.parse_args()

    def _add_opts(self):
        '''Add available arguments to argparse instance'''
        self.parser.add_argument(
            '-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='Use verbose logging')
        self.parser.add_argument(
            '-i', '--input',
            dest='input_f',
            action='store',
            metavar='X',
            help='List of directories to scan (default: targets)',
            default='targets')
        self.parser.add_argument(
            '-a', '--autofs',
            dest='autofs_f',
            action='store',
            metavar='X',
            help='Build <input_file> from <autofs_file> if it does not exist',
            default='/etc/auto.homes')
        self.parser.add_argument(
            '-c', '--config',
            dest='config_dir',
            action='store',
            metavar='X',
            help='Configuration directory (default: /etc/keyscan)',
            default='/etc/keyscan')
        self.parser.add_argument(
            '-o', '--output',
            dest='output_dir',
            action='store',
            metavar='X',
            help='Output directory for output logs (default: results/)',
            default='results/')
        self.parser.add_argument(
            '-l', '--logfile',
            dest='output_log',
            action='store',
            metavar='X',
            help='Output log for script (default: scan.log); "@" for stdout',
            default='scan.log')
        self.parser.add_argument(
            '-u', '--upload-only',
            dest='upload_only',
            action='store_true',
            help='Upload previous results and exit')
        self.parser.add_argument(
            '-d', '--delete',
            dest='delete_keys',
            action='store_true',
            help='Delete found unencrypted keys (USE WITH CAUTION)',)
        self.parser.add_argument(
            '-k', '--keep-dir',
            dest='keep_dir',
            action='store',
            metavar='X',
            help='Make a copy of key in $dir before deletion',)
        self.parser.add_argument(
            '-s', '--snapshot',
            dest='snapshot',
            action='store_true',
            help='Include files with .snapshot path (typically backups)')
        self.parser.add_argument(
            '-t', '--single-thread',
            dest='single_thread',
            action='store_true',
            help='[TESTING ONLY] Run all scans in a single thread')
        self.parser.add_argument(
            '--ssh',
            dest='limit_ssh',
            action='store_true',
            help='Limit scanning to <path>/.ssh/')
        self.parser.add_argument(
            '-b', '--base',
            dest='base_dir',
            action='store',
            metavar='X',
            help='Base directory used for key scanning (default: /scanhomes)',
            default='/scanhomes')


def main():
    '''Parse options and execute scanner'''
    # Build input file if it does not exist
    if not os.path.isfile(OPTS.input_f) and not os.path.isfile(OPTS.autofs_f):
        raise Exception('Input and autofs file do not exist')
    if not os.path.isfile(OPTS.input_f) and os.path.isfile(OPTS.autofs_f):
        QUEUE.build_input(OPTS.input_f, OPTS.autofs_f)

    # Load queue
    QUEUE.load_queue(OPTS.input_f, OPTS.output_dir)

    LOGGER.info("Scan Started")

    # Ensure output directory exists
    if not os.path.exists(OPTS.output_dir):
        os.makedirs(OPTS.output_dir)

    # Find all targets (user directories)
    targets = QUEUE.get_targets(OPTS.base_dir, OPTS.limit_ssh)

    if OPTS.single_thread:
        for target in targets:
            scan_user_directory(target)
    else:
        # Create a pool with $num_cpu processes
        pool = multiprocessing.Pool(
            processes=multiprocessing.cpu_count() * 10,
            maxtasksperchild=10)

        # Add targets to processing queue for scan_user_directory()
        pool.map_async(scan_user_directory, targets)

        # Wait for processes to complete
        pool.close()
        pool.join()

    LOGGER.info("Scan Finished")


def scan_user_directory(target):
    '''Change to target uid and initiate a scan on discovered files'''
    (user, target) = target
    user_dir = '{}/{}'.format(OPTS.base_dir, user).replace('//', '/')

    LOGGER.debug('Starting scan on %s', target)

    # Find uid owning files
    try:
        uid = get_uid(user_dir)
    except TimedOutError:
        LOGGER.warning('Timeout reached running stat on %s', user_dir)
        uid = None
    if not uid:
        return False

    # Change process effective uid to match target (nfs/root)
    try:
        os.seteuid(uid)
    except BaseException:
        LOGGER.warning('Failed to set uid for %s (%s)', user, uid)
        return False

    # Verify target directory exists
    if not os.path.isdir(target):
        LOGGER.debug('Target directory not found: %s', target)
        os.seteuid(0)
        write_log(user, 'Target directory not found: {}'.format(target))
        return None

    try:
        # Scan target for files and check for unencrypted ssh keys
        log = scan_files(target)
    except BaseException as e:
        LOGGER.warning('Uncaught Exception! :: %s', e)
        return None

    try:
        # Return effective uid back to root
        os.seteuid(0)

        # Write results to file
        write_log(user, log)
    except BaseException as e:
        LOGGER.warning(
            'Return to uid:0 failed; log for %s will not be written :: %s',
            target, e)

    # Log completed scan
    LOGGER.debug('Finished scan on %s', target)
    return None


# @timeout(20)  # Disabled because of external issue [see commit 864b44e]
def get_uid(path):
    '''Return uid from path'''
    # Check if user's home directory exists
    if not os.path.isdir(path):
        LOGGER.debug('User directory not found: %s', path)
        return False

    # Find UID of directory
    try:
        uid = os.stat(path).st_uid
    except OSError:
        LOGGER.warning('Could not get uid of directory: %s', path)
        return False
    except BaseException as e:
        LOGGER.warning('Failed scan on %s :: %s', path, e)
        return False

    return uid


def scan_files(target):
    '''Recurse through directory and initiate scan/rm on files; returns log'''
    log = {
        'target': target,
        'message': None,
        'unencrypted': [],
        'timeouts': [],
        'unknown': []}

    for root, dirs, files in os.walk(target):
        if not OPTS.snapshot:
            dirs[:] = [d for d in dirs if '.snapshot' not in d]
        for filename in files:
            path = '{}/{}'.format(root, filename)
            try:
                if not is_file(path):
                    continue
                badkey = is_unprotected(path)
            except TimedOutError:
                log['timeouts'].append(path)
                continue

            if isinstance(badkey, tuple):
                # Unknown results
                log['unknown'].append(path)
                logging.warning(
                    'SCAN ERROR: %s / %s // %s', path,
                    badkey[0].replace('\n', '\\n'),
                    badkey[1].replace('\n', '\\n'))
            elif not badkey:
                # Not a bad key
                continue

            if not OPTS.delete_keys:
                log['unencrypted'].append({
                    'path': path,
                    'removed': False})
            else:
                try:
                    if OPTS.keep_dir not in [False, None, '']:
                        save_key(path, OPTS.keep_dir)
                    # Attempt to remove file
                    os.remove(path)
                    log['unencrypted'].append({
                        'path': path,
                        'removed': True})
                except BaseException:
                    # Use None to indicate failure to remove
                    log['unencrypted'].append({
                        'path': path,
                        'removed': None})

    return log


@timeout(30)
def is_file(path):
    '''Check if path represents a regular file'''
    # Python provides a bit of magic and recurses symlinks for us
    if not os.path.exists(path):
        return False

    # Check if path is a regular file (hurray symlink recursion")
    mode = os.stat(path).st_mode
    return stat.S_ISREG(mode)


@timeout(60)
def is_unprotected(path):
    '''Check ssh key; True if bad key; (stdout, stderr) on error'''
    ssh_headers = [
        b'-----BEGIN EC PRIVATE KEY-----',
        b'-----BEGIN RSA PRIVATE KEY-----',
        b'-----BEGIN DSA PRIVATE KEY-----',
        b'-----BEGIN OPENSSH PRIVATE KEY-----']
    ssh_ok = '{}/include/is_ssh_ok'.format(
        os.path.abspath(os.path.dirname(__file__)))

    # Check for key header
    try:
        with open(path, 'rb') as fh:
            fbytes = fh.read(50)
            if not any(h in fbytes for h in ssh_headers):
                return False
    except OSError:
        # This shouldn't be possible, but prevents subprocess problems
        return None

    # Check key using external script
    # Run external 'is_ssh_ok' script on key
    process = subprocess.Popen(
        ['sudo', '-u', '#{}'.format(os.geteuid()), ssh_ok, '-k', path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Check script results
    if 'Key is Good' in stdout:
        return False
    if 'Key is BAD' in stdout:
        return True
    return (stdout, stderr)


def save_key(path, keep_dir):
    '''Read key, set euid:0, copy key to <keep_dir>, return to previus euid'''
    save_path = '{}/{}'.format(keep_dir, path).replace('//', '/')
    save_dir = os.path.dirname(save_path)

    # Save current euid
    euid = os.geteuid()

    # Read file
    with open(path, 'r') as f:
        content = f.read()

    # Write copy of key
    os.seteuid(0)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(save_path, 'w+') as f:
        f.write(content)

    # Return to previous euid
    os.seteuid(euid)


def write_log(user, log):
    '''Callback to handle log data from completed jobs'''
    logfile = '{}/{}'.format(OPTS.output_dir, user).replace('//', '/')
    with open(logfile, 'w+') as fh:

        if isinstance(log, six.string_types):
            fh.write('{}\n'.format(log))

        elif isinstance(log, dict):
            for key in log['unknown']:
                fh.write('Unknown error: {}\n'.format(key))

            for key in log['timeouts']:
                fh.write('FS hang encountered: {}\n'.format(key))

            for key_data in log['unencrypted']:
                key = key_data['path']
                removed = key_data['removed']
                if removed is True:
                    fh.write(
                        'Non-compliant key; removed: {}\n'.format(key))
                elif removed is False:
                    fh.write(
                        'Non-compliant key; NOT removed: {}\n'.format(key))
                else:
                    fh.write(
                        'Non-compliant key; REMOVAL FAILED: {}\n'.format(key))

            fh.write('Finished scanning {}\n'.format(log['target']))


def get_logger(opts):
    '''Create a log object that can be shared between instances'''
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    log_level = logging.DEBUG if opts.verbose else logging.INFO

    log = logging.getLogger(__name__)

    # Add console logging (set to error unless stdout logging)
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)
    if opts.output_log == '@':
        sh.setLevel(log_level)
    else:
        sh.setLevel(logging.ERROR)

        # If not logging to stdout, then add file handler
        fh = logging.FileHandler(opts.output_log)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
    log.addHandler(sh)
    log.setLevel(log_level)

    return log


def upload_results(results_dir, config_dir):
    datestamp = datetime.datetime.today().strftime('%Y-%m-%d_%H%M')
    prefix = socket.gethostname().split('.')[0] + '_'
    upload_config = '{}/upload.yml'.format(config_dir)

    # Load sharepoint uploader configuration
    if not os.path.exists(upload_config):
        LOGGER.error('Configuration file "%s" not found', upload_config)
        return
    with open(upload_config) as fh:
        conf = yaml.safe_load(fh)

    # Create a temporary location to compile results
    build_dir = tempfile.mkdtemp()
    results_file = '{}/{}results_{}.txt'.format(build_dir, prefix, datestamp)
    skipped_file = '{}/{}skipped_{}.txt'.format(build_dir, prefix, datestamp)

    # Create <build_dir>/<prefix>{results,skipped}.txt
    compile_results(OPTS.output_dir, results_file, skipped_file)

    # Upload constructed files
    for path in [results_file, skipped_file]:
        try:
            sp_upload(path, conf)
        except TimedOutError:
            LOGGER.error('Failed to upload results [Request Timed Out]')

    # Remove temp data
    shutil.rmtree(build_dir)


# Using globals instead of class objects because
# pickle doesn't support instance methods.
# These should *not* be used in any class.
QUEUE = Queue()
OPTS = OptsParser().parse_opts()
LOGGER = get_logger(OPTS)

if __name__ == '__main__':
    if not LockFile('/run/sshscan.pid').acquire():
        print('Lock already held; not executing')
        sys.exit(1)

    if not OPTS.upload_only:
        main()

    upload_results(OPTS.output_dir, OPTS.config_dir)
