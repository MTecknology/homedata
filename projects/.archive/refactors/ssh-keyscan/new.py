#!/usr/bin/env python
'''
Scan directories for unencrypted ssh keys and optionally delete them.
'''
import argparse
import logging
import multiprocessing
import os
import random
import signal
import six
import socket
import stat
import sys
import time

if sys.version_info.major < 3:
    import ConfigParser as configparser
else:
    import configparser

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import paramiko

# TODO:
# - add to cron
# - verify directory gets mounted
# - sync autofs file
# - Handle broken symlinks


class TimeoutError(Exception):
    def __init__(self, value='Timed Out'):
        self.value = value

    def __str__(self):
        return repr(self.value)


def timeout(seconds):
    def decorate(f):

        def handler(signum, frame):
            raise TimeoutError()

        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            old_time_left = signal.alarm(seconds)
            # never lengthen existing timer
            if 0 < old_time_left < seconds:
                signal.alarm(old_time_left)
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
            finally:
                # deduct f's run time from the saved timer
                if old_time_left > 0:
                    old_time_left -= time.time() - start_time
                signal.signal(signal.SIGALRM, old)
                signal.alarm(old_time_left)
            return result
        new_f.func_name = f.func_name
        return new_f

    return decorate


class LockFile(object):
    '''Class to handle creating and removing (pid) lockfiles'''

    # custom exceptions
    class FileLockAcquisitionError(Exception):
        pass

    class FileLockReleaseError(Exception):
        pass

    def __init__(self, path):
        self.pid = os.getpid()
        self.host = socket.gethostname()
        self.path = path

    def acquire(self):
        '''Acquire a lock, returning self if successful, False otherwise'''
        if self.islocked():
            return False
        try:
            fh = open(self.path, 'w')
            fh.write(self.addr())
            fh.close()
        except BaseException:
            if os.path.isfile(self.path):
                try:
                    os.unlink(self.path)
                except BaseException:
                    pass
            raise (self.FileLockAcquisitionError,
                   'Error acquiring lock: %s' % self.fddr())
        return self

    def release(self):
        '''Release lock, returning self'''
        if self.ownlock():
            try:
                os.unlink(self.path)
            except BaseException:
                raise (self.FileLockReleaseError,
                       'Error releasing lock: %s' % self.fddr())
        return self

    def _readlock(self):
        '''Internal method to read lock info'''
        try:
            lock = {}
            fh = open(self.path)
            data = fh.read().rstrip().split('@')
            fh.close()
            lock['pid'], lock['host'] = data
            return lock
        except BaseException:
            return {'pid': 8**10, 'host': ''}

    def islocked(self):
        '''Check if we already have a lock'''
        try:
            lock = self._readlock()
            os.kill(int(lock['pid']), 0)
            return (lock['host'] == self.host)
        except BaseException:
            return False

    def ownlock(self):
        '''Check if we own the lock'''
        lock = self._readlock()
        return (self.fddr() == self.pddr(lock))

    def __del__(self):
        '''Magic method to clean up lock when program exits'''
        self.release()

    # convenience callables for formatting
    def addr(self):
        '''Print a formatted address, "<pid>@<host>"'''
        return '{}@{}'.format(self.pid, self.host)

    def fddr(self):
        '''Print a formatted address, "<path>@<addr>"'''
        return '<{} {}>'.format(self.path, self.addr())

    def pddr(self, lock):
        '''Print a formatted address, "<path> <pid>@@<host>"'''
        return '<{} {}@{}>'.format(self.path, lock['pid'], lock['host'])


class Queue(object):
    '''Object used to maintain a queue of directories to scan'''

    def __init__(self):
        self._incomplete = list()

    def get_targets(self, prefix, append_ssh=False):
        '''Return a list of targets to scan'''
        if not self._incomplete:
            raise 'No target available'
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

        logger.debug('Skipping completed scans: %s', completed)

        self._incomplete = list(incomplete.difference(completed))
        random.shuffle(self._incomplete)

    def build_input(self, path, autofs):
        '''Build input file from autofs file'''
        with open(autofs, 'r') as _in:
            lines = _in.readlines()

        if not self.is_automount(lines):
            raise 'Provided afs file does not appear to be autofs format.'

        with open(path, 'w') as _out:
            _out.writelines(['{}\n'.format(x.split()[0])
                             for x in lines
                             if '#' not in x
                             and len(x.strip()) > 0])

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
            default='/etc/auto.scanhomes')
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


class FileUploader(object):
    '''Object to handle initialization and upload of files'''

    def __init__(self, config_dir, output_dir):
        self._conf_dir = config_dir
        self._output_dir = output_dir

        self._credentials = self._get_credentials()

    def _get_credentials(self):
        '''Read configuration file and return a configparser object'''
        creds = '{}/credentials'.format(self._conf_dir)
        # TODO: logger not global
        #if not os.path.exists(self._output_dir):
        #    logger.warning('No results (%s) to upload', self._output_dir)
        #    return None
        #if not os.path.exists(self._conf_dir):
        #    logger.warning('Config directory (%s) not found', self._conf_dir)
        #    return None
        #if not os.path.exists(creds):
        ##    logger.warning('Credentials file (%s) not found', creds)
        #    return None
        # TODO: not py2 compatible
        #if bool(os.stat(self._conf_dir).st_mode & stat.S_IROTH):
        #    logger.warning('World readable config dir (%s)', self._conf_dir)
        #    return None

        parser = configparser.ConfigParser()
        parser.read(creds)

        return {'ssh_host': parser.get('DEFAULT', 'SSH_HOST'),
                'ssh_user': parser.get('DEFAULT', 'SSH_USER'),
                'ssh_pass': parser.get('DEFAULT', 'SSH_PASS')}

    def upload_all_logs(self):
        '''Find and upload all scan logs'''
        users = os.listdir(self._output_dir)

        for user in users:
            self.upload_log(user)

    def upload_log(self, user):
        '''Upload scan result(s) to remote host'''
        path = '{}/{}'.format(self._output_dir, user)
        with open(path, 'r') as fh:
            with self._get_client() as client:
                with client.invoke_shell() as shell:
                    # TODO: Only the first line is processed when p
                    shell.send('TRANSFER^{}^{}\n'.format(
                        socket.gethostname(), user))
                    for line in fh.readlines():
                        shell.sendall(line)
                    shell.sendall('\n')

    def notify_complete(self):
        '''Notify remote host that scanning is complete and begin SP upload'''
        with self._get_client() as client:
            with client.invoke_shell() as shell:
                shell.send('UPLOAD^{}\n'.format(socket.gethostname()))

    def _get_shell(self, connection=None):
        '''Short wrapper function to return shell from connection'''
        conn = connection if connection else self._get_client()
        return conn.invoke_shell()

    def _get_client(self):
        client = paramiko.paramiko.SSHClient()
        client.connect(
                hostname=self._credentials['ssh_host'],
                username=self._credentials['ssh_user'],
                password=self._credentials['ssh_pass'])
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client


def main():
    '''Parse options and execute scanner'''
    # Build input file if it does not exist
    if not os.path.isfile(opts.input_f) and not os.path.isfile(opts.autofs_f):
        raise 'Input and autofs file do not exist'
    elif not os.path.isfile(opts.input_f) and os.path.isfile(opts.autofs_f):
        queue.build_input(opts.input_f, opts.autofs_f)

    # Load queue
    queue.load_queue(opts.input_f, opts.output_dir)

    logger.info("Scan Started")

    # Ensure output directory exists
    if not os.path.exists(opts.output_dir):
        os.makedirs(opts.output_dir)

    # Find all targets (user directories)
    targets = queue.get_targets(opts.base_dir, opts.limit_ssh)

    # Create a pool with $num_cpu processes
    pool = multiprocessing.Pool(
            processes=multiprocessing.cpu_count() * 10,
            maxtasksperchild=10)

    # Add targets to processing queue for scan_user_directory()
    pool.map_async(scan_user_directory, targets)

    # Wait for processes to complete
    pool.close()
    pool.join()

    logger.info("Scan Finished")


def scan_user_directory(target):
    '''Change to target uid and initiate a scan on discovered files'''
    (user, target) = target
    user_dir = '{}/{}'.format(opts.base_dir, user).replace('//', '/')
    log = {
        'user': user,
        'target': target,
        'message': None,
        'unencrypted': [],
        'timeouts': [],
        'unknown': []}

    logger.debug('Starting scan on %s', target)

    # Check if user's home directory exists
    if not os.path.isdir(user_dir):
        logger.warn('User directory not found: %s', user_dir)
        logger.debug('Failed scan on %s', target)
        return False

    # Find UID of directory
    try:
        uid = os.stat(user_dir).st_uid
    except OSError:
        logger.warn('Could not get uid of directory: %s', target)
        logger.debug('Failed scan on %s', target)
        return False
    except BaseException as e:
        logger.debug('Failed scan on %s :: %s', target, e)
        return False

    # Change process effective uid to match target (nfs/root)
    try:
        os.seteuid(uid)
    except BaseException as e:
        logger.warn('Failed to set uid for %s (%s)', user, uid)
        logger.debug('Failed scan on %s :: %s', target, e)
        return False

    # Verify target directory exists
    if not os.path.isdir(target):
        logger.debug('Target directory not found: %s', target)
        logger.debug('Finished scan on %s', target)
        os.seteuid(0)
        write_log(user, 'Target directory not found: {}'.format(target))
        return None

    try:
        # Scan target for files and check for unencrypted ssh keys
        for root, dirs, files in os.walk(target):
            if not opts.snapshot:
                dirs[:] = [d for d in dirs if '.snapshot' not in d]
            for filename in files:
                path = '{}/{}'.format(root, filename)
                try:
                    badkey = is_unprotected(path)
                except TimeoutError:
                    log['timeouts'].append(path)
                    continue

                if badkey is False:
                    continue
                elif badkey is None:
                    log['unknown'].append(path)
                # badkey is True

                if not opts.delete_keys:
                    log['unencrypted'].append({
                        'path': path,
                        'removed': False})
                else:
                    try:
                        #import remote_pdb; remote_pdb.RemotePdb('127.0.0.1', 4444).set_trace()
                        if opts.keep_dir not in [False, None, '']:
                            save_key(uid, path, opts.keep_dir)
                            os.seteuid(uid)
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
    except BaseException as e:
        logger.warn('Uncaught Exception! :: %s', e)

    try:
        # Return effective uid back to root
        os.seteuid(0)

        # Write results to file
        write_log(user, log)
    except BaseException as e:
        logger.warn(
            'Return to uid:0 failed; log for %s will not be written :: %s',
            target, e)

    # Upload scan results
    #TODO - breaks things
    #try:
        uploader.upload_log(user, log)
    #except BaseException as e:
    #    logger.warn('Writing log for user "%s" failed :: %s', user, e)

    # Log completed scan
    logger.debug('Finished scan on %s', target)


def write_log(user, log):
    '''Callback to handle log data from completed jobs'''
    logfile = '{}/{}'.format(opts.output_dir, user).replace('//', '/')
    with open(logfile, 'w+') as fh:

        if isinstance(log, six.string_types):
            fh.write('{}\n'.format(log))
            fh.write('Finished scanning {}\n'.format(log['target']))

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
                        'Unencrypted key; removed: {}\n'.format(key))
                elif removed is False:
                    fh.write(
                        'Unencrypted key; NOT removed: {}\n'.format(key))
                else:
                    fh.write(
                        'Unencrypted key; REMOVAL FAILED: {}\n'.format(key))

            fh.write('Finished scanning {}\n'.format(log['target']))


@timeout(2)
def is_unprotected(path):
    '''Check if path is an ssh key; True if unencrypted; None on error'''
    old_headers = [
        b'-----BEGIN EC PRIVATE KEY-----',
        b'-----BEGIN RSA PRIVATE KEY-----',
        b'-----BEGIN DSA PRIVATE KEY-----']
    new_headers = [
        b'-----BEGIN OPENSSH PRIVATE KEY-----']

    try:
        with open(path, 'rb') as fh:
            fbytes = fh.read(50)
            if any(h in fbytes for h in old_headers + new_headers):
                fh.seek(0)
                key = bytes(fh.read())
            else:
                return False
    except OSError:
        return None

    # Check for unencrypted key in old-style keys
    if any(header in fbytes for header in old_headers):
        try:
            load_pem_private_key(key, None, default_backend())
        except TypeError as e:
            if 'private key is encrypted' in str(e):
                return False
        except BaseException:
            return None
        return True

    # Check for the newer (more annoying) format
    elif any(header in fbytes for header in new_headers):
        lines = str(key).split('\n')
        key_info = lines[1] + lines[2]
        if 'none' in key_info.decode('base64'):
            return True
        return False

    # This should not be reachable
    return None


def save_key(uid, path, keep_dir):
    '''Switch euid to <uid>, read file, switch euid to 0, write backup to <keep_dir>'''
    save_path = '{}/{}'.format(keep_dir, path).replace('//', '/')
    save_dir = os.path.dirname(save_path)

    # Read file
    os.seteuid(uid)
    with open(path, 'r') as f:
        content = f.read()

    # Write File
    os.seteuid(0)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(save_path, 'w+') as f:
        f.write(content)


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


if __name__ == '__main__':
    lock = LockFile('/run/sshscan.pid').acquire()
    if not lock:
        print('Lock already held; not executing')
        sys.exit(1)

    # Using globals instead of class objects because
    # pickle doesn't support instance methods.
    # These should *not* be used in any class.
    queue = Queue()
    opts = OptsParser().parse_opts()
    uploader = FileUploader(opts.config_dir, opts.output_dir)
    logger = get_logger(opts)

    if opts.upload_only:
        uploader.upload_all_logs()
    else:
        main()
