#!/usr/bin/env python
'''
Name:
  Ingress Intel Scraper

Authors:
  Michael Lustfield <michael@profarius.com>

Description:
  This script is used to scrape data from Ingress comms.

Notes:
  * An attempt to read/write /tmp/intel_epoch is made to retain state

Requisites:
  python-bs4
  python-requests
  python-yaml
  /etc/scrape_intel.yml || ./scrape_plexts.yml
'''

import bs4
import json
import os
import random
import re
import requests
import sys
import time
import yaml


# Configuration dictionary; to be populated by load_configuration()
# Yes, I know globals are bad; deal with it or fix it.
cfg = {}


def main():
    '''Main processing of this whole script'''
    # Get login link from intel site
    login_link = get_login_link()
    if not login_link:
        print('ERR e7692c82: Unable to find login link')
        sys.exit(2)

    # Follow link to log in through Google SSO
    ses = google_login(login_link)
    if not ses:
        print('ERR f218985e: Unable to perform google login')
        sys.exit(2)

    # Make an initial get request to get "v" and csrftoken
    v = prime_requests(ses)
    if not v:
        print('ERR dc7733a5: Unable to get session value')
        sys.exit(2)

    # Get timestamp of last data retrieval
    last_epoch = get_epoch()

    # Start making requests using existing session
    while True:
        comm = request_data(ses, v, last_epoch)

        if comm == False:
            print('ERR 44c6cb31: Exiting due to bad session')
            break
        if 'result' in comm:
            # comm_count is based on returned data and NOT on non-player messages
            comm_count = len(comm['result'])
        else:
            comm_count = 0

        comms, last_epoch = process_data(comm)
        set_epoch(last_epoch)

        if len(comms) > 0:
           if cfg['output_file']:
               output_file(comms, cfg['output_file'])
           if cfg['output_logstash']:
               output_logstash(comms)

        # The typical client waits about two minutes between requests unless 50
        # 50 messages were received. Responses contain 0 to 50 comm messages.
        if comm_count <= 20:
            time.sleep(120)
        elif comm_count <= 49:
            time.sleep(90)


def load_configuration():
    ''' Reads /etc/scrape_intel.yml to pull configuration data and updates the
        global 'cfg' variable because I'm too lazy to make something better.'''
    global cfg

    cfg = {
      'random_requests': True,
      'save_state': True,
      'timestamp_file': '/tmp/intel_epoch',
      'std_headers': {
          'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'DNT': '1'},
      'users': {},
      'output_file': '',
      'output_logstash': '',
      'area': {
          'min': { 'lon': -180000000, 'lat': -90000000 },
          'max': { 'lon': 180000000, 'lat': 90000000 }}}

    try:
        for fname in ['/etc/scrape_plexts.yml', './scrape_plexts.yml']:
            if os.path.isfile(fname):
                cfg.update(yaml.load(open(fname, 'r').read()))
    except:
        print('ERR 7501cb12: Unable to load /etc/scrape_intel.yml')
        sys.exit(1)

    if len(cfg['users']) <= 0:
        print('ERR ade12ef7: No users found in /etc/scrape_intel.yml; aborting')
        sys.exit(1)

    user = random.randint(0, len(cfg['users']) - 1)
    cfg['user'] = cfg['users'].keys()[user]
    cfg['pass'] = cfg['users'][cfg['user']]


def get_epoch():
    '''Return last epoch time from file if it exists'''
    try:
        with open(cfg['timestamp_file'], 'r') as fh:
            epoch = fh.read()
            fh.close()
    except:
        print('ERR aac91f75: Unable to load previous timestamp; using current time')
        return int(time.time())

    if epoch.strip() == '':
        print('ERR b32dac77: Unable to load previous timestamp; using current time')
        return int(time.time())

    return int(epoch)


def set_epoch(epoch):
    '''Write the last epoch checked to file'''
    try:
        with open(cfg['timestamp_file'], 'w') as fh:
            fh.write(str(epoch))
            fh.close()
    except:
        print('ERR 26ef6484: Unable to write timestamp to file')


def get_login_link():
    ''' Opens the ingress intel site without credentials
        Returns a link with a toket to bring to google'''
    try:
        req = requests.get('https://www.ingress.com/intel', headers=cfg['std_headers'])
    except:
        print('ERR d6a0a4fe: Error occurred when trying to reach intel site')
        return False

    if req.status_code != 200:
        print('ERR 9d93441a: Unexpected response code')
        return False

    m = re.search(r'(https.+?ServiceLogin.+?)"', req.content)
    if m:
        return m.group(1)
    else:
        return False


def google_login(login_link):
    ''' Follows a link to google sso and performs the authentication ritual
        Returns a session to bring back to intel website or False on failure'''
    # Creates a session object for future requests
    ses = requests.Session()

    # Retrieves the first form for authentication
    try:
        req = ses.get(login_link, headers=cfg['std_headers'])
    except:
        print('ERR dccfe7c2: Error occurred when trying to reach google login')
        return False

    if req.status_code != 200:
        print('ERR fff3d585: Unexpected response code')
        return False

    # Grab data from the response for the next request
    bs = bs4.BeautifulSoup(req.content)

    # Parse the form to pick out fields for the next request
    postbody = {}
    for item in bs.find('form').find_all('input'):
        if item.get('name') and item.get('value'):
            postbody[item.get('name')] = item.get('value').encode('utf-8').strip()
        postbody['Email'] = cfg['user']

    # Make the second request in the sequence
    try:
        req = ses.post(bs.find('form').get('action'), data=postbody, headers=cfg['std_headers'])
    except:
        print('ERR b5221199: Error occcured when trying to reach stage two of google login')
        return False

    if req.status_code != 200:
        print('ERR 225ece87: Unexpected response code')
        return False

    # Grab data from the response for the second request
    bs = bs4.BeautifulSoup(req.content)

    # Parse the form to pick out fields for the second request
    postbody = {}
    for item in bs.find('form').find_all('input'):
        if item.get('name') and item.get('value'):
            postbody[item.get('name')] = item.get('value').encode('utf-8').strip()
        postbody['Passwd'] = cfg['pass']

    # Make the third request in the sequence (getting fun...)
    try:
        req = ses.post(bs.find('form').get('action'), data=postbody, headers=cfg['std_headers'])
    except:
        print('ERR f9665cf7: Error occcured when trying to reach stage two of google login')
        return False

    if req.status_code != 200:
        print('ERR 4242c599: Unexpected response code')
        return False

    # We should now have a response that can be sent back to ingress
    return ses


def prime_requests(ses):
    ''' This initial authenticated requests ensures we get a csrftoken cookie set
        as well as locates the "v" to be used in future requests'''
    try:
        req = ses.get('https://www.ingress.com/intel', headers=cfg['std_headers'])
    except:
        print('ERR b59d9fac: Error occurred when trying to reach intel site')
        return False

    if req.status_code != 200:
        print('ERR 124d8c4f: Unexpected response code')
        return False

    m = re.search(r'gen_dashboard_([^\.]+).js', req.content, re.MULTILINE)
    if m:
        return m.group(1)
    else:
        return False


def dummy_requests(ses):
    '''Performs dummy requests to the intel site to mimic traffic'''
    #TODO
    pass


def request_data(ses, v, epoch):
    '''Request global data from ingress site'''
    headers = cfg['std_headers']
    headers['Referer'] = 'https://www.ingress.com/intel'
    headers['Content-Type'] = 'application/json; charset=utf-8'
    headers['X-CSRFToken'] = ses.cookies['csrftoken']

    # Global Requests
    requestbody = {
        'minLatE6': cfg['area']['min']['lat'],
        'minLngE6': cfg['area']['min']['lon'],
        'maxLatE6': cfg['area']['max']['lat'],
        'maxLngE6': cfg['area']['max']['lon'],
        'minTimestampMs': epoch,
        'maxTimestampMs': -1,
        'tab': 'all',
        'v': v}

    try:
        req = ses.post('https://www.ingress.com/r/getPlexts', data=json.dumps(requestbody), headers=headers)
    except:
        print('ERR: 467fdf68: Unable to get plext data')
        return False

    return json.loads(req.content)


def process_data(data):
    ''' Process a collection of communication results
        Return a tuple (<comms>, <epoch>) where:
            comms: list of dictionaries of communication data
            epoch: epoch timestamp of last processed message'''
    comms = []
    last_epoch = -1
    if 'result' in data:
        for r_id, r_epoch, r_plext in data['result']:
            comm = parse_data(r_id, r_plext['plext'], r_epoch)
            if r_epoch > last_epoch:
                # Add one ms to ensure we're requesting new data (1000=1s)
                last_epoch = r_epoch + 1
            if comm:
                comms.append(comm)
    return (comms, last_epoch)


def parse_data(rid, plext, epoch):
    '''Takes plext data and returns an object more suitable for lucene storage'''

    categories = plext['categories']
    markup = plext['markup']
    plextType = plext['plextType']
    team = plext['team']
    text = plext['text']

    comm = {
        'meta_id': rid,
        'meta_categories': categories,
        'meta_type': plextType,
        'meta_epoch': epoch,
        'meta_faction': team}

    # Player Messages
    if comm['meta_type'] == 'PLAYER_GENERATED':
        return False

    # Niantic Messages
    # We're given a list of lists so is gets a little interesting
    elif comm['meta_type'] == 'SYSTEM_BROADCAST':
        if len(markup) == 6 and [ k for k, v in markup] == ['PLAYER', 'TEXT', 'PORTAL', 'TEXT', 'TEXT', 'TEXT']:

            # Created Control Field
            if 'created a Control Field' in markup[1][1]['plain']:
                comm = parse_created_field(comm, markup)

            # Destroyed Control Field
            elif 'destroyed a Control Field' in markup[1][1]['plain']:
                comm = parse_destroyed_field(comm, markup)

            else:
                comm['meta_ERROR'] = '7f742b61'

        elif len(markup) == 5 and [ k for k, v in markup] == ['PLAYER', 'TEXT', 'PORTAL', 'TEXT', 'PORTAL']:

            # Link Portals
            if 'linked' in markup[1][1]['plain']:
                comm = parse_created_link(comm, markup)

            # Destroyed Link
            elif 'destroyed the Link' in markup[1][1]['plain']:
                comm = parse_destroyed_link(comm, markup)

            else:
                comm['meta_ERROR'] = 'd751e5b7'

        elif len(markup) == 5 and [ k for k, v in markup] == ['TEXT', 'PORTAL', 'TEXT', 'TEXT', 'TEXT']:

            # Field Decayed
            # Note, there will be THREE messages for a decayed field; one per portal
            if 'has decayed' in markup[2][1]['plain']:
                comm = parse_field_decayed(comm, markup)

            else:
                comm['meta_ERROR'] = '7ae812ef'

        elif len(markup) == 3 and [ k for k, v in markup] == ['PLAYER', 'TEXT', 'PORTAL']:

            # Captured Portal
            if 'captured' in markup[1][1]['plain']:
                comm = parse_captured_portal(comm, markup)

            # Destroyed Resonator
            elif 'destroyed a Resonator' in markup[1][1]['plain']:
                comm = parse_destroyed_resonator(comm, markup)

            # Deployed Resonator
            elif 'deployed a Resonator' in markup[1][1]['plain']:
                comm = parse_deployed_resonator(comm, markup)

            # Deployed Fracker
            elif 'deployed a Portal Fracker' in markup[1][1]['plain']:
                comm = parse_deployed_fracker(comm, markup)

            # Deployed Beacon
            elif 'deployed a Beacon' in markup[1][1]['plain']:
                comm = parse_deployed_beacon(comm, markup)

            else:
                comm['meta_ERROR'] = '9244e225'

        else:
            comm['meta_ERROR'] = 'b3497e1d'

    else:
        comm['meta_ERROR'] = '3fbbae68'

    if 'meta_ERROR' in comm:
        # Can use either markup or json.dumps(markup)
        # JSON is best when sending to ELK; markup is best when debugging
        comm['UNPROCESSED_DATA'] = markup # TODO json.dumps(markup)
        comm['UNMATCHED_KEY'] = markup[1][1]['plain']

    return comm


def parse_created_field(comm, markup):
    '''Parse message for: Create Control Field'''
    comm['action_performed'] = 'created_field'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    comm['portal_field_mu'] = markup[4][1]['plain']
    return comm


def parse_destroyed_field(comm, markup):
    '''Parse message for: Destroyed Control Field'''
    comm['action_performed'] = 'destroyed_field'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    comm['portal_field_mu'] = markup[4][1]['plain']
    return comm


def parse_created_link(comm, markup):
    '''Parse message for: Link Portals'''
    comm['action_performed'] = 'created_link'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    comm = parse_common_portal(comm, markup[4][1])
    return comm


def parse_destroyed_link(comm, markup):
    '''Parse message for: Destroyed Link'''
    comm['action_performed'] = 'destroyed_link'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    comm = parse_common_portal(comm, markup[4][1])
    return comm


def parse_captured_portal(comm, markup):
    '''Parse message for: Captured Portal'''
    comm['action_performed'] = 'captured_portal'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    return comm


def parse_destroyed_resonator(comm, markup):
    '''Parse message for: Destroyed Resonator'''
    comm['action_performed'] = 'destroyed_resonator'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    return comm


def parse_deployed_resonator(comm, markup):
    '''Parse message for: Deployed Resonator'''
    comm['action_performed'] = 'deployed_resonator'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    return comm


def parse_deployed_fracker(comm, markup):
    '''Parse message for: Deployed Fracker'''
    comm['action_performed'] = 'deployed_fracker'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    return comm


def parse_deployed_beacon(comm, markup):
    '''Parse message for: Deployed Beacon'''
    comm['action_performed'] = 'deployed_beacon'
    comm = parse_common_player(comm, markup)
    comm = parse_common_portal(comm, markup[2][1])
    return comm


def parse_field_decayed(comm, markup):
    '''Parse message for: Decayed Field'''
    comm['action_performed'] = 'field_decayed'
    comm = parse_common_portal(comm, markup[1][1])
    comm['portal_field_mu'] = markup[3][1]['plain']
    return comm


def parse_common_player(comm, markup):
    '''Common message parsing for: Player'''
    comm['player_name'] = markup[0][1]['plain']
    comm['player_faction'] = markup[0][1]['team']
    return comm


def parse_common_portal(comm, portal):
    '''Common message parsing for: Portal'''
    comm['portal_address'] = portal['address']
    comm['portal_latitude'] = portal['latE6']
    comm['portal_longitude'] = portal['lngE6']
    comm['portal_name'] = portal['name']
    comm['portal_plain'] = portal['plain']
    comm['portal_faction'] = portal['team']
    return comm

    comm['dest_portal_faction'] = markup[4][1]['team']
    return comm


def output_logstash(comms):
    '''Sends comm data to logstash'''
    #TODO
    pass


def output_file(comms, output_file = './out_file.json'):
    '''Appends json output to <output_file>'''
    # Can be loaded with json.loads(open('./out_file.json', 'r').replace(']\n[', ','))
    with open(output_file, 'a') as f:
        f.write(json.dumps(comms) + '\n')
        f.close()


if __name__ == '__main__':
    load_configuration()
    main()
