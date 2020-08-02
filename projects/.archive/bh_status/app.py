#!/usr/bin/python
'''
Provides information about status of services running on boothost.

Requires: uwsgi, uwsgi-plugin-python, python-bottle
'''

import bottle
import os
import re
import subprocess

app = application = bottle.Bottle()


@app.route('/')
@app.route('/bh_status')
def show_main():
    '''
    Return the main login form.
    '''
    results = [
        check_service('smbstatus'),
        check_service('ads'),
        check_service('home_perms'),
        check_service('crypt_emar'),
        check_service('crypt_home'),
        check_service('ping')]
    return bottle.jinja2_template('results.html', results=results)

@app.route('/service/<service>')
@app.route('/bh_status/service/<service>')
def show_service_status(service):
    '''
    Check status of a single service and provide a simple return.
    '''
    results = [check_service(service)]
    return bottle.jinja2_template('results.html', results=results)


@app.route('/simple/<service>')
@app.route('/bh_status/simple/<service>')
def show_service_status(service):
    '''
    Check status of a single service and provide a simple return.
    '''
    if check_service(service)['status'] == 'good':
        return 'SUCCESS'
    else:
        return 'FAILURE'


def check_service(service):
    '''
    Check status of a single service.
    Return:
      {
        status: <good|warn|error>
        title: <text>
        description: <text>
        details: <details>
      }
    '''
    if service == 'smbstatus':
        return check_service_smb()
    elif service == 'ads':
        return check_service_ads()
    elif service == 'home_perms':
        return check_service_homeperms()
    elif service == 'crypt_emar':
        return check_service_cryptemar()
    elif service == 'crypt_home':
        return check_service_crypthome()
    elif service == 'ping':
        return check_service_ping()
    else:
        return {
            'status': 'error',
            'title': 'Unknown',
            'description': 'No Description',
            'details': 'No Details'}


def check_service_smb():
    '''
    Check status of smbstatus.
    '''
    status = 'good'

    child = subprocess.Popen(
        ['sudo', 'smbstatus', '-b'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()

    output = ''
    for line in stdout.split('\n'):
        try:
            if '-1' in line:
                output += '<span style="color: #A79600;">' + line + '</span>\n'
            else:
                output += line + '\n'
        except:
            pass

    if stderr is not '':
        output += '\n<span style="color: #A79600;">STDERR:\n' + stderr + '</span>\n'

    if 'Failed' in output:
        status = 'error'
    elif '-1' in output:
        status = 'error'
    elif child.returncode != 0:
        status = 'error'

    return {
        'status': status,
        'title': 'smbstatus',
        'description': 'Samba Service Status',
        'details': output}


def check_service_ads():
    '''
    Check status of net ads testjoin.
    '''
    status = 'good'

    child = subprocess.Popen(
        ['sudo', 'net', 'ads', 'testjoin'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()

    output = stdout
    if stderr is not '':
        output += '\n<span style="color: #A79600;">STDERR:\n' + stderr + '</span>\n'

    if child.returncode != 0:
        status = 'error'

    return {
        'status': status,
        'title': 'ads',
        'description': 'Samba AD Join Status',
        'details': output}


def check_service_homeperms():
    '''
    Check status of home directory permissions.
    '''
    status = 'good'

    child = subprocess.Popen(
        ['ls -ld /home/[0-9][0-9][0-9]0/*'],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()

    output = ''
    for line in stdout.split('\n'):
        try:
            real_usr = line.split()[2]
            real_grp = line.split()[3]
            correct_usr = line.split('/')[3]
            correct_grp = line.split('/')[2]
            if correct_usr == 'inactive':
                output += line + '\n'
            elif real_usr.isdigit():
                if status == 'good':
                    status = 'warn'
                output += '<span style="color: #A79600;">' + line + '</span>\n'
            elif not re.match('[0-9]{3}0', real_grp):
                if status == 'good':
                    status = 'warn'
                output += '<span style="color: #A79600;">' + line + '</span>\n'
            elif correct_usr != real_usr:
                status = 'error'
                output += '<span style="color: #FF0000;">' + line + '</span>\n'
            elif correct_grp != real_grp:
                status = 'error'
                output += '<span style="color: #FF0000;">' + line + '</span>\n'
            else:
                output += line + '\n'
        except:
            pass

    if stderr is not '':
        output += '\n<span style="color: #A79600;">STDERR:\n' + stderr + '</span>\n'

    if child.returncode != 0:
        status = 'error'

    return {
        'status': status,
        'title': 'home_perms',
        'description': 'User Home Directories',
        'details': output}


def check_service_cryptemar():
    '''
    Check status of emar encrypted partition.
    '''
    if os.path.ismount('/var/www/emar'):
        status = 'good'
    else:
        status = 'error'

    child_1 = subprocess.Popen(
        ['mount'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    child_2 = subprocess.Popen(
        ['grep', 'emar'],
        stdin = child_1.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = child_2.communicate()

    return {
        'status': status,
        'title': 'crypt_emar',
        'description': 'EMAR Encrypted Storage',
        'details': stdout}


def check_service_crypthome():
    '''
    Check status of home encrypted partition.
    '''
    if os.path.ismount('/home'):
        status = 'good'
    else:
        status = 'error'

    child_1 = subprocess.Popen(
        ['mount'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    child_2 = subprocess.Popen(
        ['grep', 'home'],
        stdin = child_1.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = child_2.communicate()

    return {
        'status': status,
        'title': 'crypt_home',
        'description': 'Home Directory Encrypted Storage',
        'details': stdout}


def check_service_ping():
    '''
    Check connectivity between the BH and NC.
    '''
    child = subprocess.Popen(
        ['ping', '-n', '-c', '4', '-i', '0.2', '-W', '0.5', '-w', '4', '172.16.4.2'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()

    if '0% packet loss' in stdout:
        status = 'good'
    elif '100% packet loss' in stdout:
        status = 'error'
    else:
        status = 'warning'

    return {
        'status': status,
        'title': 'ping',
        'description': 'Ping NS1',
        'details': stdout}


class StripPathMiddleware(object):
    '''
    Get that slash out of the request
    This is only needed when run with ./app.py
    '''
    def __init__(self, a):
        self.a = a
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)


if __name__ == '__main__':
    bottle.run(app=StripPathMiddleware(app),
        host='0.0.0.0',
        port=8080)
