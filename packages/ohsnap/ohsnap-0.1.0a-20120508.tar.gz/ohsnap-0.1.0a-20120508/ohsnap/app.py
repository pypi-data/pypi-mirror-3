#!/usr/bin/env python
"""
A module to house the ohsnap application classes.
"""

from archive import Archive
from ext import SubCommandApp

from prettytable import PrettyTable
from subprocess import Popen, PIPE
import re, time
import datetime

class OhsnapApp(SubCommandApp):
    """The ohsnap application class which inherits cli.log.LoggingApp"""
    snapcmd = '/usr/local/bin/tarsnap -C ~ -c -f "`date -u`" documents vault'

    def pre_run(self):
        """
        Configures the application prior to self.run()

        Sets the tarsnap binary path based on the the --binary parameter
        """
        super(OhsnapApp, self).pre_run()
        self.binary = self.base.params.binary
    
    def get_archives(self):
        """Fetch the tarsnap archive list and create Archive objects for each
        that is ohsnap formatted"""
        self.log.debug('Fetching archive list')
        p = Popen("%s --list-archives" % self.binary, shell=True, stdout=PIPE)
        stdout = p.communicate()[0]
        archive_list = map(
            lambda a: Archive(a),
            filter(
                lambda s: s.startswith('ohsnap:'),
                stdout.strip().split('\n')
            )
        )
        return sorted(archive_list, key=lambda a: a.time)

class OhsnapBackupApp(OhsnapApp):
    def snap(self):
        """Create an ohsnap formatted backup"""
        full_name = "ohsnap:%d:%s:%s" % (int(time.time()), 
                self.params.retention, self.params.name)
        snap_command = "%s -C %s -c -f '%s' %s" % (self.binary, self.params.cwd, full_name,
                ' '.join(self.params.path))
        self.log.debug("Executing tarsnap command: %s" % snap_command)
        p = Popen(snap_command, shell=True)
        p.communicate()

class OhsnapListApp(OhsnapApp):

    def list_archives(self):
        """Create and print prettytable containing a list of all Archives 
        sorted by creation date"""
        fields = ['Name', 'Retention', 'Creation Date']
        table = PrettyTable(fields)
        for field in fields:
            table.set_field_align(field, 'l')
        for archive in self.get_archives():
            self.log.debug("Found archive: %s" % archive)
            table.add_row([archive.name, archive.retention,
                archive.time_string()])
        print table

class OhsnapPurgeApp(OhsnapApp):
    def purge_archives(self):
        for archive in self.get_archives():
            self.log.debug("Found archive: %s" % archive)

            res = {
                'seconds': 's',
                'minutes': 'm',
                'hours': 'h',
                'days': 'd',
                'weeks': 'w',
                'months': 'M',
                'years': 'y',
            }
            delta_dict = {}

            for key, value in res.items():
                match = re.search('(\d+)%s' % value, archive.retention)
                if match:
                    delta_dict[key] = int(match.group(1))
         
            delta_dict.setdefault('days', 0)

            if 'months' in delta_dict:
                delta_dict['days'] += delta_dict['months'] * 30
                del delta_dict['months']

            if 'years' in delta_dict:
                delta_dict['days'] += delta_dict['years'] * 365
                del delta_dict['years']

            delta = datetime.timedelta(**delta_dict)

            if (archive.time + delta.total_seconds()) < time.time():
                self.log.info("Purging archive: %s" % archive)
                purge_command = "%s -d -f '%s'" % (self.binary, 
                        archive.full_name)
                self.log.debug("Executing tarsnap command: %s" % purge_command)
                p = Popen(purge_command, shell=True)
                p.communicate()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
