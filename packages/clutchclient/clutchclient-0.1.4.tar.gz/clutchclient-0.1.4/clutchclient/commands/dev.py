import httplib
import os
import posixpath
import signal
import subprocess
import sys
import threading
import time
import urllib
import urlparse
import webbrowser

from clutchclient.utils import json, get_config, remote_call, get_app_slug

from clutchclient.commands import APP_PARSER

TUNNEL_URL = 'https://tunnel.clutch.io/'

TUNNEL_POLL_URL = 'https://tunnel.clutch.io/poll/'
TUNNEL_POST_URL = 'https://tunnel.clutch.io/post/'

def _translate_path(initial_path, path):
    # abandon query parameters
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    path = posixpath.normpath(urllib.unquote(path))
    words = path.split('/')
    words = filter(None, words)
    path = initial_path
    for word in words:
        drive, word = os.path.splitdrive(word)
        head, word = os.path.split(word)
        if word in (os.curdir, os.pardir):
            continue
        path = os.path.join(path, word)
    return path

def poll(username, password, app_slug, **kwargs):
    headers = kwargs.get('headers', {})
    headers.update({
        'Accept': 'application/json',
        'X-Clutch-Username': username,
        'X-Clutch-Password': password,
        'X-Clutch-App-Slug': app_slug,
    })
    parsed_url = urlparse.urlparse(TUNNEL_POLL_URL)
    if parsed_url.scheme == 'http':
        conn_class = httplib.HTTPConnection
    else:
        conn_class = httplib.HTTPSConnection
    conn = conn_class(parsed_url.netloc)
    conn.request('GET', parsed_url.path, '', headers)
    try:
        response = conn.getresponse()
    except (IOError, httplib.HTTPException):
        # Something busted on the server side, sleep 1 second and try again.
        time.sleep(1)
        return {}
    raw_data = response.read()
    conn.close()
    try:
        return json.loads(raw_data)
    except ValueError:
        # Something busted on the server side, sleep 2 seconds and try again.
        time.sleep(2)
        return {}

def post(path, uuid):
    if isinstance(path, basestring):
        try:
            with open(path, 'r') as f:
                data = f.read().encode('utf-8')
        except IOError:
            data = 'CLUTCH404DOESNOTEXIST'
    else:
        data = json.dumps(path)
    headers = {'Accept': 'application/json'}
    parsed_url = urlparse.urlparse(TUNNEL_POST_URL)
    if parsed_url.scheme == 'http':
        conn_class = httplib.HTTPConnection
    else:
        conn_class = httplib.HTTPSConnection
    conn = conn_class(parsed_url.netloc)
    conn.request('POST', parsed_url.path + uuid, data, headers)
    response = conn.getresponse()
    raw_data = response.read()
    conn.close()
    return json.loads(raw_data)

def serve(initial_path, username, password, app_slug):
    print 'Serving at https://tunnel.clutch.io/view/%s/%s/' % (
        username,
        app_slug,
    )
    while 1:
        data = poll(username, password, app_slug)
        for item in data.get('files', []):
            if 'dir' in item:
                print 'GET', '/'
                listing = []
                for d in os.listdir(initial_path):
                    idx = os.path.join(initial_path, d, 'index.html')
                    if os.path.exists(idx):
                        listing.append(d)
                t = threading.Thread(target=post, args=[listing, item['uuid']])
                t.start()
            else:
                print 'GET', item['path']
                path = _translate_path(initial_path, item['path'])
                t = threading.Thread(target=post, args=[path, item['uuid']])
                t.start()

def send_reload_message(filename, username, app_slug, password, **kwargs):
    headers = kwargs.get('headers', {})
    headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    parsed_url = urlparse.urlparse(TUNNEL_URL)
    if parsed_url.scheme == 'http':
        conn_class = httplib.HTTPConnection
    else:
        conn_class = httplib.HTTPSConnection
    conn = conn_class(parsed_url.netloc)
    print filename
    data = json.dumps({
        'password': password,
        'message': {'changed_file': filename},
    })
    path = '/event/%s/%s/' % (username, app_slug)
    conn.request('POST', path, data, headers)
    response = conn.getresponse()
    raw_data = response.read()
    conn.close()
    return raw_data

def create_monitor_thread(path, username=None, app_slug=None, password=None):
    sleep_time = 1 # check every second

    mtimes = {}

    # Pre-fill the mtimes dictionary
    paths = [path]
    while len(paths):
        hidden = '%s.' % (os.sep,)
        for root, dirs, files in os.walk(paths.pop()):
            if hidden in root:
                continue
            for d in dirs:
                if d.startswith('.'):
                    continue
                normdir = os.path.join(root, d)
                if os.path.islink(normdir):
                    paths.append(normdir)
            for fn in files:
                if fn.startswith('.'):
                    continue
                filename = os.path.join(root, fn)
                mtimes[filename] = os.path.getmtime(filename)
    
    def _monitor():
        while 1:
            paths = [path]
            while len(paths):
                hidden = '%s.' % (os.sep,)
                for root, dirs, files in os.walk(paths.pop()):
                    if hidden in root:
                        continue
                    for d in dirs:
                        if d.startswith('.'):
                            continue
                        normdir = os.path.join(root, d)
                        if os.path.islink(normdir):
                            paths.append(normdir)
                    for fn in files:
                        if fn.startswith('.'):
                            continue
                        filename = os.path.join(root, fn)
                        mt = os.path.getmtime(filename)
                        old_mt = mtimes.get(filename)
                        mtimes[filename] = mt
                        if old_mt != mt:
                            trimmed = filename[len(path) + len(os.sep):]
                            print 'Detected change in %s, sending reload message' % (trimmed,)
                            send_reload_message(trimmed, username, app_slug,
                                password)
            time.sleep(sleep_time)
    
    return _monitor

def start_weinre():
    URL = 'http://cloud.github.com/downloads/callback/callback-weinre/weinre-jar-1.6.1.zip'
    if not os.path.exists('/tmp/weinre-jar/weinre.jar'):
        print 'Installing javascript debugging tool'
        proc = subprocess.Popen(['curl', '-O', URL], cwd='/tmp')
        proc.communicate()
        proc = subprocess.Popen(['unzip', '-x', 'weinre-jar-1.6.1.zip'],
            cwd='/tmp')
        proc.communicate()
    cmd = ['java', '-jar', '/tmp/weinre-jar/weinre.jar',
        '--boundHost', '-all-', '--reuseAddr', 'true', '--httpPort', '41676']
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    def _open_browser():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:41676/client/#anonymous')
    threading.Thread(target=_open_browser).start()

    return proc

def handle(namespace, extra):
    APP_PARSER.add_argument('-w', '--weinre', dest='weinre', action='store_true', default=False)
    APP_PARSER.add_argument('-t', '--no-toolbar', dest='toolbar', action='store_false', default=True)
    namespace = APP_PARSER.parse_args()

    dirname = os.path.abspath(os.path.expanduser(namespace.directory))

    app_slug = get_app_slug(namespace)

    config = get_config(namespace)

    def _ping_dev():
        url = '%sview/%s/%s/' % (TUNNEL_URL, config['username'], app_slug)
        while 1:
            remote_call(config, 'start_dev',
                app_slug=app_slug,
                url=url,
                toolbar=namespace.toolbar,
            )
            time.sleep(240) # Wait 4 Minutes

    ping_dev_thread = threading.Thread(target=_ping_dev)
    ping_dev_thread.daemon = True
    ping_dev_thread.start()

    func = create_monitor_thread(dirname,
        app_slug=app_slug,
        username=config['username'],
        password=config['password']
    )
    watch_change_thread = threading.Thread(target=func)
    watch_change_thread.daemon = True
    watch_change_thread.start()

    if namespace.weinre:
        proc = start_weinre()

        def _term(signum, frame):
            proc.kill()
            sys.exit(1)

        signal.signal(signal.SIGTERM, _term)

    try:
        print 'Starting up development server'
        serve(dirname, config['username'], config['password'], app_slug)
    except KeyboardInterrupt:
        print '\nTearing down development server'
        remote_call(config, 'stop_dev', app_slug=app_slug)
    
    if namespace.weinre:
        proc.kill()