import argparse
import contextlib
import os
import re
import sys
import tempfile
import urllib2
import zipfile

from StringIO import StringIO

SKELETON_URL = 'http://clutchdownloads.s3.amazonaws.com/skeletons/app.zip'

PARSER = argparse.ArgumentParser(
    description='Command-line interface for clutch.io')
PARSER.add_argument('command')
PARSER.add_argument('dirname')

SLUG_RE = re.compile(r'^[\w-]+$')

def handle(namespace, extra):
    namespace = PARSER.parse_args()

    if SLUG_RE.search(namespace.dirname) is None:
        print >> sys.stderr, 'Sorry, you specified an invalid directory name'
        sys.exit(1)
    
    if namespace.dirname.lower() in ('global', 'clutch-core'):
        print >> sys.stderr, 'Sorry, both "global" and "clutch-core" are reserved names'
        sys.exit(1)
    
    dirname = os.path.abspath(os.path.expanduser(namespace.dirname))
    if os.path.exists(dirname):
        print >> sys.stderr, 'Sorry, a directory by that name already exists'
        sys.exit(1)

    d = urllib2.urlopen(SKELETON_URL)

    # First we extract the zip file into a temporary directory
    tmp = StringIO(d.read())
    extracted = tempfile.mkdtemp()
    zip_context = contextlib.closing(
        zipfile.ZipFile(tmp, 'r', zipfile.ZIP_DEFLATED))
    with zip_context as z:
        z.extractall(extracted)
    
    # Delete any DELETEME.txt files
    for root, dirs, files in os.walk(extracted):
        for fn in files:
            if fn.endswith('DELETEME.txt'):
                os.unlink(os.path.join(root, fn))
    
    # Now we rename it to the user's desired directory
    os.rename(extracted, dirname)