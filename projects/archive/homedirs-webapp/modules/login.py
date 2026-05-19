#!/usr/bin/env python

# Helper functions for handling user sessions

import bottle
import ldap


def process_login(session):
    '''
    Process the login attempt and either set the session or return to login page
    '''
    try:
        username = bottle.request.POST.get('username', '').strip()
        password = bottle.request.POST.get('password', '').strip()
        if not username or not password:
            return bottle.jinja2_template('login.html', message='Invalid Credentials')
        ad = ldap.open('ad.domain.tld')
        ad.simple_bind_s('DOMAIN\\{}'.format(username), password)
    except ldap.INVALID_CREDENTIALS:
        return bottle.jinja2_template('login.html', message='Invalid Credentials')
    except:
        return bottle.jinja2_template('login.html', message='Unknown Error')
    else:
        ad_r = ad.search('OU=Staff,OU=Users,DC=ad,DC=domain,DC=tld', ldap.SCOPE_SUBTREE, 'CN={}'.format(username), None)
        rt, rd = ad.result(ad_r, 0)
        if rt != 100:
            return bottle.jinja2_template('login.html', message='Unknown Error')
        session['gid'] = rd[0][1]['gidNumber'][0]
        session['username'] = rd[0][1]['cn'][0]
        session['full_name'] = rd[0][1]['displayName'][0]
        session['center'] = rd[0][1]['physicalDeliveryOfficeName'][0]
        session['uid'] = rd[0][1]['uidNumber'][0]
        if 'foo' in rd[0][1]['memberOf']:
            session['filemover'] = 'True'
        elif 'bar' in rd[0][1]['memberOf']:
            session['filemover'] = 'True'
        else:
            session['filemover'] = 'False'

        if session['filemover'] == 'True':
            bottle.redirect('/move')
        else:
            bottle.redirect('/files')

