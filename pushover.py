#!/usr/bin/env python2
#
# Zabbix alert script for Pushover
# (c) 2016, Entertainment Media Group AG
# License: MIT
#

from __future__ import print_function

import httplib
import os.path
import urllib
from ConfigParser import RawConfigParser
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sys import stderr, exit

# parse cli argumennts
parser = ArgumentParser(description='Zabbix Pushover Client', version='0.2',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-c', nargs='?', default=os.path.dirname(os.path.abspath(__file__)) + '/pushover.cfg',
                    help='The configuration file to use')
parser.add_argument('to', help="Receiving user's key")
parser.add_argument('subject', help='Message subject')
parser.add_argument('message', help='Message body')
args = parser.parse_args()

# read config
if not os.path.exists(args.c):
    print('Could not find configuration file: ' + args.c, end='\n', file=stderr)
    exit(1)

config = RawConfigParser()
config.read(args.c)

# send API request
options = {
    'token': config.get('pushover', 'token'),
    'user': args.to,
    'title': args.subject,
    'message': args.message,
    'priority': config.get('pushover', 'priority')
}

if config.get('pushover', 'priority') == 2:
    options['retry'] = config.get('pushover', 'retry')
    options['expire'] = config.get('pushover', 'expire')

if config.has_option('section', 'sound') and len(config.get('pushover', 'sound')) > 0:
    options['sound'] = config.get('pushover', 'sound')

conn = httplib.HTTPSConnection('api.pushover.net:443')
conn.request(
    'POST',
    '/1/messages.json',
    urllib.urlencode(options),
    {'Content-type': 'application/x-www-form-urlencoded'}
)

res = conn.getresponse()

if res.status != 200:
    print('Pushover API returned error: ' + res.read(), end='\n', file=stderr)
    exit(1)
