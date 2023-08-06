import getpass
import httplib
import os
import plistlib
import sys
import urlparse

try:
    import simplejson as json
    dir(json) # placate pyflakes
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError('Sorry, we could not find a json library on your system. Please install simplejson: http://simplejson.readthedocs.org/')

REMOTE_URL = 'https://rpc.clutch.io/rpc/'

def set_config(namespace):
    while 1:
        username = raw_input('What is your clutch.io username? ').strip()
        password = getpass.getpass('What is your clutch.io password? ').strip()

        un_pass_dict = {'username': username, 'password': password}
        auth = remote_call(un_pass_dict, 'authenticate', **un_pass_dict)
        if not auth:
            print 'The username and password you provided were invalid, please try again.'
            continue
        if not auth.get('user'):
            print 'The username and password you provided were invalid, please try again.'
            continue
        break
    filename = os.path.expanduser(namespace.config)
    data = {
        'username': username,
        'password': password,
    }
    with open(filename, 'w') as f:
        d = json.dumps(data, indent=4, sort_keys=True)
        f.write(d)
        f.flush()
    return data

def get_config(namespace):
    filename = os.path.expanduser(namespace.config)
    try:
        with open(filename, 'r') as f:
            data = json.loads(f.read())
    except Exception:
        return set_config(namespace)
    if not data.get('username'):
        return set_config(namespace)
    if not data.get('password'):
        return set_config(namespace)
    return data

def remote_call(config, command, **kwargs):
    headers = kwargs.get('headers', {})
    headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Clutch-Username': config['username'],
        'X-Clutch-Password': config['password'],
    })
    parsed_url = urlparse.urlparse(REMOTE_URL)
    if parsed_url.scheme == 'http':
        conn_class = httplib.HTTPConnection
    else:
        conn_class = httplib.HTTPSConnection
    conn = conn_class(parsed_url.netloc)
    data = json.dumps({
        'method': command,
        'params': kwargs,
        'id': 1, # Dummy value, we don't need to correlate
    })
    conn.request('POST', parsed_url.path, data, headers)
    response = conn.getresponse()
    raw_data = response.read()
    conn.close()
    data = json.loads(raw_data)
    if data.get('error'):
        raise ValueError(data['error'])
    return data['result']

def get_app_slug(namespace):
    if namespace.app:
        return namespace.app
    cwd = os.path.abspath(os.path.realpath(os.getcwd()))
    plist_path = os.path.join(cwd, 'clutch.plist')
    if not os.path.exists(plist_path):
        print >> sys.stderr, 'Couldn\'t find clutch.plist, are you sure you\'re in an app directory?'
        sys.exit(1)
    plist = plistlib.readPlist(plist_path)
    app = plist.get('ClutchAppShortName')
    if not app:
        print >> sys.stderr, 'App short name not found in clutch.plist, and no app short name specified using -a'
        sys.exit(1)
    return app