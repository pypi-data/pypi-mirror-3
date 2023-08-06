import argparse
import os

CLUTCH_CONF = '~/.clutchio'

PARSER = argparse.ArgumentParser(
    description='Command-line interface for clutch.io')
PARSER.add_argument('command')
PARSER.add_argument('-c', '--config', dest='config', action='store', nargs='?', default=CLUTCH_CONF)

APP_PARSER = argparse.ArgumentParser(
    description='Command-line interface for clutch.io')
APP_PARSER.add_argument('command')
APP_PARSER.add_argument('-a', '--app', dest='app', action='store', nargs='?')
APP_PARSER.add_argument('-c', '--config', dest='config', action='store', nargs='?', default=CLUTCH_CONF)
APP_PARSER.add_argument('-d', '--directory', dest='directory', action='store', nargs='?', default=os.getcwd())

from clutchclient.commands.dev import handle as dev
from clutchclient.commands.upload import handle as upload
from clutchclient.commands.startapp import handle as startapp
from clutchclient.commands.startscreen import handle as startscreen
from clutchclient.commands.version import handle as version

# Placate PyFlakes
def __exported_functionality__():
    return [dev, upload, startapp, startscreen, version]