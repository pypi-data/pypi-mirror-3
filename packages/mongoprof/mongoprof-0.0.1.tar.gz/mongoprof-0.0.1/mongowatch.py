#!/usr/bin/env python
__version__ = '0.0.1'

import time
import datetime
import argparse

from pymongo import Connection
from termcolor import colored

def watch(dbname, refresh):
    db = getattr(Connection('localhost'), dbname)
    db.set_profiling_level(2)
    last_ts = datetime.datetime.utcnow()
    date_fmt = '%H:%M:%S'
    exclude_name = '{0}.system.profile'.format(dbname)
    while True:
        for e in db.system.profile.find({'ns': {'$ne': exclude_name},
                                         'ts': {'$gt': last_ts}}):
            output = []
            output.append(colored('{ts:%H:%M:%S}'.format(**e), 'white'))
            output.append(colored('{ns}'.format(**e), 'blue'))
            if e['op'] == 'query':
                output.append(colored('{query}'.format(**e), 'cyan'))
            elif e['op'] == 'getmore':
                output.append(colored('getmore {query}'.format(**e), 'grey'))
            elif e['op'] == 'command':
                output.append(colored('{command}'.format(**e), 'cyan'))
            else:
                output.append('unknown operation: {op}'.format(**e), 'red')
            if 'nscanned' in e:
                output.append(colored('scanned {nscanned}'.format(**e), 'yellow'))
            if 'ntoskip' in e:
                output.append(colored('skip {ntoskip}'.format(**e), 'blue'))
            if 'nreturned' in e:
                output.append(colored('returned {nreturned}'.format(**e), 'green'))
            if e.get('scanAndOrder'):
                output.append(colored('scanAndOrder', 'red'))
            output.append(colored('{millis}ms'.format(**e), 'green'))
            print ' '.join(output)
            last_ts = e['ts']
        time.sleep(refresh)
    db.set_profiling_level(0)
    db.system.profile.drop()

def main():
    parser = argparse.ArgumentParser(description='watch mongo queries')
    parser.add_argument('dbname', help='name of database to watch')
    args = parser.parse_args()
    watch(args.dbname, 0.1)

if __name__ == '__main__':
    main()

