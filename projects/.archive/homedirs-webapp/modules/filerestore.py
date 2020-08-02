#!/usr/bin/env python

# Helper functions for the file restore section.

import bottle
import email
import glob
import json
import os
import re
import redis
import smtplib
import socket
import time

from collections import OrderedDict
from itertools import groupby
from rq.decorators import job
from rq.job import Job
from xml.etree import ElementTree

redis_conn = redis.Redis(db=2)


def show_user_files(session, scope):
    '''
    Display a list of files to the user
    '''
    if not session.get('uid'):
        bottle.redirect('/login')

    # Get list of user files; Job will be sent to the background
    j = get_files.delay(session.get('username'), session.get('center'), scope)

    # Send a page to the user with the Job ID
    return bottle.jinja2_template('files.html', job_id=j.id)


def process_restore_request(session):
    '''
    Get files for a backup and get the files to the user
    '''
    if not session.get('uid'):
        bottle.redirect('/login')

    files = bottle.request.POST.getall('files')
    accepted = bottle.request.POST.get('accepted', '').strip()
    if bottle.request.POST.get('in_place', '').strip() == 'on':
        in_place = True
    else:
        in_place = False

    if accepted == 'cancel':
        bottle.redirect('/files')

    if len(files) > 10:
        return bottle.jinja2_template('error.html', errmsg='Too many files were selected. Limit: 10')
    if len(files) == 0:
        return bottle.jinja2_template('error.html', errmsg='No files were selected')

    if accepted != 'restore':
        filelist = []
        for filename in files:
            m = re.sub('([^/]*/){5}', '', filename)
            filelist.append({'name': filename, 'trimmed': m})
        return bottle.jinja2_template('confirm_restore.html', files=filelist)
    elif accepted == 'restore':
        job = run_restore.delay(session.get('username'), session.get('center'), files, in_place)
        msg = 'Restore request has been queued as job ID: {}<br />Keep track of this ID.<br /><a href="/logout">Log Out</a>'.format(job.get_id())
        return bottle.jinja2_template('error.html', errmsg=msg)


def apireq_jobdata():
    '''
    Takes a json request for the status/data of a Job ID. {'job_id': 'xyz'}
    returns:
      {'job_id': 'xyz', 'status': ('finished'|'running'|'failed'), 'data': ('none'|'foobarbuz')}
    '''
    bottle.response.content_type = 'application/json'

    jbody = json.load(bottle.request.body)

    job_id = jbody['job_id']
    j = Job.fetch(job_id, connection=redis_conn)

    if not j.is_finished and j.get_status() != 'failed':
        return json.dumps({'job_id': job_id, 'status': 'running', 'data': 'none'})

    r = j.result

    if type(r) == dict:
        return json.dumps({'job_id': job_id, 'status': 'failed', 'data': r['ERR']})
    if type(r) != str:
        return json.dumps({'job_id': job_id, 'status': 'failed', 'data': 'Unknown error searching for documents'})

    return json.dumps({'job_id': job_id, 'status': 'finished', 'data': r})

@job('gethomedirs', connection=redis_conn, result_ttl=300, timeout=300)
def get_files(username, center, scope):
    '''
    Get the files available to be restored by the user.
    scope: user, shared, all
    '''
    user_home = glob.glob('/srv/homedirs/*/{0}/{1}'.format(center, username))
    user_shared = glob.glob('/srv/homedirs/*/shared/{0}'.format(center))

    if len(user_home) != 1:
        user_home = glob.glob('/srv/homedirs/{0}/{0}/{1}'.format(center, username))
        if len(user_home) != 1:
            return {'ERR': 'Could not find a proper home directory for username'}

    if len(user_shared) != 1:
        return {'ERR': 'Too many shared drives for center were found'}

    rh = user_home[0].split('/')
    rs = user_shared[0].split('/')

    if scope == 'user':
        files = dict([build_dict('menu', get_dir_list(user_home[0]), '')])['menu']
        if files == {}:
            return {'ERR': 'No files for username were found'}
        return build_xml(files, rh)

    elif scope == 'shared':
        shared = dict([build_dict('menu', get_dir_list(user_shared[0]), '')])['menu']
        if shared == {}:
            return {'ERR': 'No files for shared drive were found'}
        return build_xml(shared, rs)

    elif scope == 'all':
        files = dict([build_dict('menu', get_dir_list(user_home[0]), '')])['menu']
        if 'ERR' in files.keys():
            return files
        shared = dict([build_dict('menu', get_dir_list(user_shared[0]), '')])['menu']
        if 'ERR' in shared.keys():
            return shared
        files[rh[0]][rh[1]][rh[2]][rh[3]][rh[4]][rh[5]]['Shared'] = shared[rs[0]][rs[1]][rs[2]][rs[3]][rs[4]][rs[5]]
        return build_xml(files, rh)


def get_dir_list(path):
    '''
    Returns a list of of files in the path.
    '''
    filelist = []
    for root, dirs, files in os.walk(path):
        for name in files:
            filelist.append(os.path.join(root, name))
    return filelist


def build_dict(group, items, path):
    sep = lambda i:i.split('/', 1)
    head = [i for i in items if len(sep(i))==2]
    tail = [i for i in items if len(sep(i))==1]
    gv = groupby(sorted(head), lambda i:sep(i)[0])
    return group, dict([(i, path+i) for i in tail] + [build_dict(g, [sep(i)[1] for i in v], path+g+'/') for g,v in gv])


def build_xml(dictionary, root):
    '''
    Remove the root of the dictionary and then build the form.
    '''
    listing = dictionary[root[0]][root[1]][root[2]][root[3]][root[4]][root[5]]
    listing = OrderedDict(sorted(listing.items(), key=lambda t: t[0]))

    return ElementTree.tostring(dict_to_xml(listing))


def dict_to_xml(dict_, parent_node=None, parent_name=''):
    def node_for_value(name, value, parent_node, parent_name, cls):
        '''
        Create <li><input><label>...</label></input></li> elements
        Return the <li> element
        '''
        value = os.path.join(parent_name, value)
        node = ElementTree.SubElement(parent_node, 'li')
        child = ElementTree.SubElement(node, 'input')
        child.set('type', 'checkbox')
        child.set('id', value)
        child.set('value', value)
        if cls == 'file':
            child.set('name', 'files')
        child = ElementTree.SubElement(child, 'label')
        child.set('for', value)
        child.set('class', cls)
        child.text = name
        return node


    # create an <ul> element to hold all child elements
    if parent_node is None:
        node = ElementTree.Element('ul')
        node.set('id', 'master')
    else:
        node = ElementTree.SubElement(parent_node, 'ul')

    # add the sub-elements
    dict_ = OrderedDict(sorted(dict_.items(), key=lambda t: t[0]))
    for key, value in dict_.iteritems():
        if isinstance(value, dict):
            child = node_for_value(key, key, node, parent_name, cls='directory')
            dict_to_xml(value, child, key)
        else:
            node_for_value(key, value, node, parent_name, cls='file')

    return node


@job('filerestore', connection=redis_conn, result_ttl=1300, timeout=900)
def run_restore(user, center, files, in_place):
    if not verify_files(user, center, files):
        notify_user(user, 'Could not restore files. You do not have access to one or more of the files requested.')
        return None

    if in_place:
        success, response = push_files(user, center, files)
        if success:
            #notify_user FAILED
            pass
        else:
            pass
            #notify_user SUCCESS
    else:
        success, archive = build_archive(files)
        if not success:
            #notify_user FAILED
            pass
        else:
            success = push_archive(user, center, archive)
            if not success:
                #notify_user FAILED
                pass
            else:
                #notify_user SUCCESS
                pass
            remove_archive(archive)


def verify_files(user, center, files):
    '''
    Make sure user has access to restore requested files.
    Will return False if they should not be restoring any of these files.
    '''
    for f in files:
        pass
        # Make sure any user restores are owned by that user
        # Make sure any shared restores are for that users center
        # Make sure restores happen for shared underneath Protected
    return True


def push_files(user, center, files):
    '''
    Push files to center
    '''
    pass


def build_archive(files):
    '''
    Build a zip archive of files to restore.
    Will return a path to that zip file.
    '''
    pass


def push_archive(user, center, archive):
    '''
    Push archive to users desktop
    '''
    pass


def remove_archive(archive):
    '''
    Delete zip archive.
    '''
    if archive is not None:
        pass


def notify_user(user, message):
    '''
    Send a notification to the user via email.
    '''
    fromaddr = 'noreply@{}'.format(socket.getfqdn())
    toaddr = '{}@good-sam.com'.format(str(user))
    msg = email.MIMEText.MIMEText(message)
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'File Restore Request'

    try:
        smtpObj = smtplib.SMTP('email.good-sam.com')
        smtpObj.sendmail(fromaddr, [toaddr], msg.as_string())
    except:
        pass
