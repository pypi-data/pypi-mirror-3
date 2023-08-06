import contextlib
import httplib
import os
import sys
import urlparse
import zipfile

from StringIO import StringIO

from clutchclient.utils import json, get_config

from clutchclient.commands import APP_PARSER

UPLOAD_URL = 'https://rpc.clutch.io/rpc/upload/'

def _post_zip_file(config, app_slug, in_file):
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
    body = '\r\n'.join([
        '--' + boundary,
        'Content-Disposition: form-data; name="archive"; filename="archive.zip"',
        'Content-Type: application/zip',
        '',
        in_file.getvalue(),
        '--' + boundary + '--',
        ''
    ])
    headers = {
        'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
        'Accept': 'application/json',
        'X-App-Slug': app_slug,
        'X-Clutch-Username': config['username'],
        'X-Clutch-Password': config['password'],
    }
    parsed_url = urlparse.urlparse(UPLOAD_URL)
    if parsed_url.scheme == 'http':
        conn_class = httplib.HTTPConnection
    else:
        conn_class = httplib.HTTPSConnection
    conn = conn_class(parsed_url.netloc)
    conn.request('POST', parsed_url.path, body, headers)
    response = conn.getresponse()
    raw_data = response.read()
    conn.close()
    data = json.loads(raw_data)
    if data.get('error'):
        raise ValueError(data['error'])
    return data['result']

def handle(namespace, extra):
    namespace = APP_PARSER.parse_args()

    config = get_config(namespace)

    dirname = os.path.abspath(os.path.expanduser(namespace.directory))

    if not os.path.isdir(dirname):
        error_msg = 'Sorry, but %s is not a directory' % (dirname,)
        print >> sys.stderr, error_msg
    
    cwd = os.path.abspath(os.path.realpath(os.getcwd()))
    if not os.path.exists(os.path.join(cwd, 'clutch.plist')):
        print >> sys.stderr, 'Couldn\'t find clutch.plist, are you sure you\'re in an app directory?'
        sys.exit(1)

    tmp = StringIO()

    zip_context = contextlib.closing(
        zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED))

    with zip_context as z:
        paths = [dirname]
        while len(paths):
            hidden = '%s.' % (os.sep,)
            for root, dirs, files in os.walk(paths.pop()):
                if hidden in root:
                    continue
                for d in dirs:
                    normdir = os.path.join(root, d)
                    if os.path.islink(normdir):
                        paths.append(normdir)
                for fn in files:
                    if fn.startswith('.'):
                        continue
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(dirname) + len(os.sep):] #XXX: relative path
                    z.write(absfn, zfn)

    resp = _post_zip_file(config, namespace.app, tmp)
    del tmp

    print 'Uploaded new version: %s' % (resp,)