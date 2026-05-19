#!/usr/bin/env python

# Helper functions for the file mover section.

import bottle
import datetime
import operator
import pytz
import time

from rqfunc import *


def build_filemove_cmd(action, cur_user, new_user, cur_center, new_center):
    '''
    Build the command used for running file mover from provided input
    '''
    errmsg = None

    if not action or action == 'none':
        errmsg = 'You broke something! No action selected.'
    elif action == 'namechange':
        if not cur_user or not new_user or not cur_center:
            errmsg = 'You broke something! Fields are missing.'
        else:
            cmd = ['filemover', '-a', action, '-u', cur_user, '-c', cur_center, '-n', new_user]
    elif action == 'centerchange':
        if not cur_user or not cur_center or not new_center:
            errmsg = 'You broke something! Fields are missing.'
        else:
            cmd = ['filemover', '-a', action, '-u', cur_user, '-c', cur_center, '-n', new_center]
    elif action == 'termmove':
        if not cur_user or not new_user or not cur_center:
            errmsg = 'You broke something! Fields are missing.'
        else:
            cmd = ['filemover', '-a', action, '-u', cur_user, '-c', cur_center, '-n', new_user]
    else:
        errmsg = 'You broke something!'

    if errmsg:
        return (False, errmsg)
    else:
        return (True, cmd)


def show_move_request(session):
    '''
    Show the file mover form
    '''
    if not session.get('uid'):
        bottle.redirect('/login')

    if session.get('filemover') == 'False':
        return bottle.jinja2_template('error.html', errmsg='You do not have access to this area.')

    jobs = get_all_jobs('filemover')
    for k, v in jobs.iteritems():
        jobs[k]['desc'] = v['description'].split('[')[1].split(']')[0].replace(',', '').replace("'", '')
        dt = datetime.datetime.strptime(jobs[k]['created_at'], '%Y-%m-%dT%H:%M:%Sz')
        lt = pytz.timezone('UTC').localize(dt).astimezone(pytz.timezone('America/Chicago'))
        jobs[k]['created_at'] = lt.strftime('%m/%d/%Y %H:%M:%S')

    sorted_jobs = sorted(jobs.values(), key=operator.itemgetter('enqueued_at'), reverse=True)

    return bottle.jinja2_template('move.html', jobs=sorted_jobs)


def process_move_request(session):
    '''
    Execute the file move request
    '''
    if not session.get('uid'):
        bottle.redirect('/login')

    if session.get('filemover') == 'False':
        return bottle.jinja2_template('error.html', errmsg='You do not have access to this area.')

    # Grab post params
    action = bottle.request.POST.get('action', '').strip()
    curusr = bottle.request.POST.get('curusr', '').strip()
    newusr = bottle.request.POST.get('newusr', '').strip()
    curcnt = bottle.request.POST.get('curcnt', '').strip()
    newcnt = bottle.request.POST.get('newcnt', '').strip()
    accepted = bottle.request.POST.get('accepted', '').strip()

    if accepted == 'cancel':
        bottle.redirect('/move')

    # Build file move command
    ret, cmd = build_filemove_cmd(action, curusr, newusr, curcnt, newcnt)
    if not ret:
        return bottle.jinja2_template('error.html', errmsg=cmd)

    # If this is a center change, then we need check size
    # unless the size was already accepted (yes, this is an intentional back door)
    if action == 'centerchange' and accepted != 'yup':
        # Make sure the user directory exists
        if os.path.isdir('/srv/homedirs/{0}/{0}/{1}'.format(curcnt, curusr)):
            user_dir = '/srv/homedirs/{0}/{0}/{1}'.format(curcnt, curusr)
        elif os.path.isdir('/srv/homedirs/{0}/{0}/inactive/{1}'.format(curcnt, curusr)):
            user_dir = '/srv/homedirs/{0}/{0}/inactive/{1}'.format(curcnt, curusr)
        else:
            msg = 'Unable to queue job. The source data can\'t be found.<br /><a href="/move">Continue</a>'
            return bottle.jinja2_template('error.html', errmsg=msg)

        # Get size of users current data
        j = get_size.delay(user_dir)
        while True:
            if j.is_finished:
                break
        time.sleep(1)
        r = j.result
        if type(r) != int:
            return bottle.jinja2_template('error.html', errmsg='Unable to calculate size!')
        size = r / 1000000

        # Check size before transferring
        if size > 800:
            msg = 'Unable to queue job. Users home directory is larger than 800MB.<br /><a href="/move">Continue</a>'
            # larger than 300MB; will not execute
            return bottle.jinja2_template('error.html', errmsg=msg)
        elif size > 50 and accepted != 'yup':
            # larger than 50MB; need confirmation
            return bottle.jinja2_template('confirm_move.html', dat={'action': action, 'curusr': curusr,
                'curcnt': curcnt, 'newusr': newusr, 'newcnt': newcnt, 'size': size})
        else:
            job = run_filemover_cmd.delay(cmd)
    else:
        # Not a center change, all file moving is local
        job = run_filemover_cmd.delay(cmd)

    # If we made it here, the job is in queue
    if job:
        msg = 'Job successfully queued as job ID: {}<br /><a href="/move">Continue</a>'.format(job.get_id())
        return bottle.jinja2_template('error.html', errmsg=msg)
