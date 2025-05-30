#!/usr/bin/env python3
'''
Simple web utility that performs basic networking probes.
'''
import bottle
import subprocess


# Entry point
application = bottle.app()


@bottle.route('/static/<filename:path>')
def static(filename):
    '''
    Serve static files.
    '''
    return bottle.static_file(filename, root='./static')


@bottle.get('/')
def show_form():
    '''
    Redirect the user according to their session.
    '''
    return bottle.template('index')

@bottle.get('/<start_tab>')
def show_form_at(start_tab):
    '''
    Redirect the user according to their session.
    '''
    if start_tab not in ['dig', 'iperf', 'ping']:
        bottle.abort(404, 'Tab does not exist.')
    return bottle.template('index', tab=start_tab)


@bottle.post('/')
def run_query():
    '''
    Redirect the user according to their session.
    '''
    form_data = bottle.request.POST

    command = build_command(form_data)
    output = subprocess.run(
            command, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return bottle.template(
            'index', results=output.stdout, tab=form_data['operation'])


def build_command(form):
    '''
    Build the command that was requested.
    '''
    match form.get('operation'):

        case 'dig':
            if form['record_type'] not in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']:
                bottle.abort(400, 'Invalid record_type')
            return ['dig', form['target'],
                   f"{form['record_type']}",
                   f"@{form['dig_server']}"]

        case 'iperf':
            if 1024 > int(form['port']) > 65535:
                bottle.abort(400, 'Invalid iperf_port')
            if 15 > int(form['duration']) > 90:
                bottle.abort(400, 'Invalid iperf_time')
            return ['iperf3', '-c', form['target'],
                   '-p', form['port'],
                   '-t', form['duration']]

        case 'ping':
            if 0 > int(form['ping_count']) > 100:
                bottle.abort(400, 'Invalid ping_count')
            return ['ping', '-c', form['ping_count'], form['target']]

    bottle.abort(400, 'Unexpected command requested')


if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=8080)
