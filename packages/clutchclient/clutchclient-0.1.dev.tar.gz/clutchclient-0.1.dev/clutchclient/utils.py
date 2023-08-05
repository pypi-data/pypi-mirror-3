import getpass
import httplib
import os
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
    username = raw_input('What is your clutch.io username? ').strip()
    password = getpass.getpass('What is your clutch.io password? ').strip()
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