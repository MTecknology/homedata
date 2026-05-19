#!/usr/bin/env python

import bottle
import bottle_session
import redis

from modules.filemove import show_move_request, process_move_request
from modules.filerestore import show_user_files, process_restore_request, apireq_jobdata
from modules.login import process_login


app = application = bottle.Bottle()
redis_conn = redis.Redis(db=2)
session_plugin = bottle_session.SessionPlugin(cookie_lifetime=600, keyword='session')
app.install(session_plugin)


@app.route('/static/<filename:path>')
def static(filename):
    '''Serve static files'''
    return bottle.static_file(filename, root='./static')

## Main Page ###

@app.route('/')
def index(session):
    '''Redirect the user according to their session'''
    uid = session.get('uid')
    if uid:
        bottle.redirect('/files')
    else:
        bottle.redirect('/login')

## User Login ##

@app.get('/login')
def show_login(session):
    '''Show the login page'''
    return bottle.jinja2_template('login.html')


@app.post('/login')
def do_login(session):
    '''Process the login attempt and either set the session or return to login page'''
    return process_login(session)


@app.route('/logout')
def do_logout(session):
    '''Process a log out request'''
    session.destroy()
    bottle.redirect('/login')

## File Restore ##

@app.get('/files')
def show_files(session):
    '''Display a list of files to the user'''
    return show_user_files(session, 'user')


@app.get('/files/user')
def do_file_restore(session):
    '''Get files for a backup and get the files to the user'''
    return show_user_files(session, 'user')


@app.get('/files/shared')
def do_file_restore(session):
    '''Get files for a backup and get the files to the user'''
    return show_user_files(session, 'shared')


@app.get('/files/all')
def do_file_restore(session):
    '''Get files for a backup and get the files to the user'''
    return show_user_files(session, 'all')


@app.post('/files')
def do_file_restore(session):
    '''Get files for a backup and get the files to the user'''
    return process_restore_request(session)

@app.post('/files/job_status')
def get_job_data():
    '''Return a json paylod with the status of the requested Job ID'''
    # {'job_id': 'xyz'}
    return apireq_jobdata()

## File Mover ##

@app.get('/move')
def show_move(session):
    '''Show the file mover form'''
    return show_move_request(session)


@app.post('/move')
def do_file_move(session):
    '''Execute the file move request'''
    return process_move_request(session)

## Misc ##

if __name__ == '__main__':
    bottle.run(app=app, host='0.0.0.0', port=80)
