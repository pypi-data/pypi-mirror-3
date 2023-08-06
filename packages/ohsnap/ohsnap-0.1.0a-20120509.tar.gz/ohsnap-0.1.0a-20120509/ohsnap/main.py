#!/usr/bin/env python

from app import *
from ext import BaseCommandApp
from subprocess import Popen, PIPE

@BaseCommandApp
def ohsnap(app):
    if app.params.command == 'backup':
        backup.run()
    if app.params.command == 'list':
        list.run()
    if app.params.command == 'purge':
        purge.run()

ohsnap.add_param('command', help='subcommand to perform', choices=('backup', 'list',
    'purge'), default=None, type=str)
ohsnap.add_param('-b', '--binary', help= 'path to the tarsnap binary', 
        default='/usr/local/bin/tarsnap', type=str)

@OhsnapBackupApp(base=ohsnap)
def backup(app):
    app.snap()

backup.add_param('path', nargs='*', help='paths to backup')
backup.add_param('-C', '--cwd', help='directory to run the backup from',
        default='./', type=str)
backup.add_param('-n', '--name', help='archive name', default=None, type=str)
backup.add_param('-r', '--retention', 
        help='integer and time identifier e.g. 1h, 3d, 6y', default='1m', type=str)

@OhsnapListApp(base=ohsnap)
def list(app):
    app.list_archives()

@OhsnapPurgeApp(base=ohsnap)
def purge(app):
    app.purge_archives()

def run():
    ohsnap.run()

if __name__ == '__main__':
    run()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

