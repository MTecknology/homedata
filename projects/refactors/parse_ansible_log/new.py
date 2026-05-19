#!/usr/bin/env python
'''
This script takes the path name to an ansible log, parses
the data, and produces a more digestible form.
'''
import logging
import re
import sys


# Map object for parsing ansible log data
parse_map = [
    # success
    {   'key': re.compile('unreachable=0\s+failed=0'),
        'log': 'successful',
        'lvl': 'success'},
    # unreachable
    {   'key': re.compile('uthent'),
        'log': 'authentication error',
        'lvl': 'unreachable'},
    {   'key': re.compile('Name or service not known'),
        'log': 'DNS Error',
        'lvl': 'unreachable'},
    {   'key': re.compile('timed out'),
        'log': 'timed out',
        'lvl': 'unreachable'},
    {   'key': re.compile('SSH protocol'),
        'log': 'ssh protocol',
        'lvl': 'unreachable'},
    {   'key': re.compile('Unable to connect to port 22'),
        'log': 'Unable to connect to port 22',
        'lvl': 'unreachable'},
    {   'key': re.compile('Network is unreachable'),
        'log': 'Network is unreachable',
        'lvl': 'unreachable'},
    # failed
    {   'key': re.compile('cache_update'),
        'log': 'apt error',
        'lvl': 'failed'},
    {   'key': re.compile('simplejson error'),
        'log': 'simplejson error',
        'lvl': 'failed'},
    {   'key': re.compile('arch\.rc'),
        'log': 'simplejson error',
        'lvl': 'failed'},
    {   'key': re.compile('is listed more than once'),
        'log': 'Repo is listed more than once',
        'lvl': 'failed'},
    {   'key': re.compile('python2 bindings for rpm'),
        'log': 'python2 bindings for rpm',
        'lvl': 'failed'},
    {   'key': re.compile('found available'),
        'log': 'No package matching',
        'lvl': 'failed'},
    {   'key': re.compile('repomd\.xml'),
        'log': 'HTTP Error 404',
        'lvl': 'failed'},
    {   'key': re.compile('baseurl'),
        'log': 'Cannot find a valid baseurl',
        'lvl': 'failed'},
    {   'key': re.compile('yum_base'),
        'log': "YumBase' object has no attribute 'preconf'",
        'lvl': 'failed'},
    {   'key': re.compile('\/bin\/python'),
        'log': 'Unsupported python version',
        'lvl': 'failed'},
]


def main():
    '''
    Read contents of csv file and print a summary of data
    '''
    if len(sys.argv) != 2:
        logging.critical('Exactly one argument (input file) is supported')
        sys.exit(1)
    results = parse_log(sys.argv[1])
    if not results:
        logging.critical('Error reading log data')
        sys.exit(1)
    print_results(results)


def parse_log(path):
    '''
    Read the contents of a file and turn it into pretty data
    '''
    data = read_file(path)
    if not data:
        return None
    hosts = read_hosts(data)
    return parse_results(hosts)


def read_hosts(log_data):
    '''
    Read host information from log data
    '''
    hosts = {}

    for num, line in enumerate(log_data):
        if 'RECAP' in line:
            logonly = log_data[:num]
            results = log_data[(num + 1):]

    for line in results:
        hostname = line.split()[5]
        hosts[hostname] = []
        hosts[hostname].append(line.strip())

    for host in hosts.keys():
        for line in logonly:
            if host in line:
                hosts[host].append(line.strip())

    return hosts


def parse_results(hosts):
    '''
    Read host data and return a results in the form dict( 'key': list(), )
    '''
    results = {
        'unreachable': {},
        'failed': {},
        'unknown': {},
        'success': {}}

    for host, log in hosts.items():
        inmap = False
        for pmap in parse_map:
            if pmap['key'].search(log[-1]):
                results[pmap['lvl']][host] = pmap['log']
                inmap = True
                break
            if not inmap:
                results['unknown'][host] = 'Unknown: {}'.format(log[-1])

    return results


def print_results(results):
    '''
    Print parsed ansible results
    '''
    for status, rset in results.items():
        if status == 'success':
            continue
        for host, res in rset.items():
            print('{}#{}'.format(host, res))


    print('\nCounts:')
    for status, rset in results.items():
        print('  {}: {}'.format(status.ljust(14), len(rset)))


def read_file(path):
    '''
    Return raw list of log data
    '''
    try:
        with open(path, 'rb') as log_file:
            return log_file.readlines()
    except IOError:
        logging.warning('Path does not exist: %s', path)
        return None


if __name__ == '__main__':
    main()
