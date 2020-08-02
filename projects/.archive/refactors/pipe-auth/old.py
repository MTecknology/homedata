#!/usr/bin/env python

import sys
import urllib
import urllib2
import pickle
import base64

AUTH_ALL = 0
AUTH_ALL = 1

# compare to: /usr/share/doc/jabberd2/pipe-auth.pl

USER_DOMAIN = 'domain.tld'
DEVICE_DOMAIN = 'rpd.domain.tld'
API = {USER_DOMAIN: 'authenticate_user', DEVICE_DOMAIN: 'authenticate_device'}
API_HOST = '10.220.1.220'


def xmpp_unescape(input):
    valid = (' ', '"', '&', '\'', '/', ':', '<', '>', '@', '\\')
    out = []
    start = 0
    while True:
        ind = input.find('\\', start)
        if ind == -1:
            out.append(input[start:])
            break
        out.append(input[start:ind])
        if ind + 2 < len(input):
            try:
                char = chr(int(input[ind + 1:ind + 3], 16))
                if char in valid:
                    out.append(char)
                    start = ind + 3
                    continue
            except:
                pass
        out.append(input[ind])
        start = ind + 1
    return ''.join(out)


def ok(*args):
    if len(args) == 1:
        print 'OK %s\n' % args[0]
    else:
        print 'OK\n'
    sys.stdout.flush()


def no(*args):
    print 'NO\n'
    sys.stdout.flush()


def choice(val):
    if isinstance(val, unicode):
        ok(val)
    elif val:
        ok()
    else:
        no()


def free(*args):
    sys.exit(0)


def is_ascii(s):
    try:
        s.encode('ascii')
        return True
    except:
        return False


def check_password(args):
    if len(args) != 3:
        no()
        return

    try:
        defs = {'username': xmpp_unescape(args[0]), 'password': args[1], 'domain': args[2]}
        defs['api'] = API.get(defs['domain'])
        defs['api_host'] = API_HOST
        if not defs['api']:
            no()
            return
        opener = urllib2.build_opener()
        decoded = base64.b64decode(args[1])
        if is_ascii(decoded):
            opener.addheaders.append(('Cookie', 'sessionid=%s' % decoded))
        f = opener.open('http://%(api_host)s:8080/api/1/%(api)s/?format=pickle' % defs, data=urllib.urlencode(defs))
        resp = f.read()
        choice(pickle.loads(resp))
    except:
        # If we don't return something on check password, we crash the server.
        # Catch all exceptions and print no()
        import traceback
        traceback.print_exc(None, open('/var/tmp/pipe-auth.exc', 'a'))
        no()


if AUTH_ALL:
    cmds = {'OK': ok, 'USER-EXISTS': ok, 'CHECK-PASSWORD': ok, 'FREE': free}
else:
    cmds = {'OK': ok, 'USER-EXISTS': ok, 'CHECK-PASSWORD': check_password, 'FREE': free}


def main():
    #    print " ".join(cmds.keys()) + "\n"
    # Apparently this order is important
    print "OK USER-EXISTS CHECK-PASSWORD FREE\n"

    sys.stdout.flush()

    line = sys.stdin.readline()
    while line:
        args = line.split()

        if (len(args) > 0):
            cmd = args[0]
            if cmd in cmds:
                cmds[cmd](args[1:])
            line = sys.stdin.readline()

if __name__ == '__main__':
    while True:
        try:
            main()
        except IOError:
            # We get IOErrors if c2s has gone away, which leaves pipe-auth spinning
            # Just exit in this case.
            sys.exit(1)
        except:
            import traceback
            import exceptions
            traceback.print_exc(None, open('/var/tmp/pipe-auth.exc', 'a'))
            if sys.exc_info()[0] == exceptions.SystemExit:
                break
