#!/usr/bin/env python

import time

class Archive():
    """A class to represent ohsnap formatted tarsnap archives"""

    def __init__(self, full_name):
        """Initialize the object by splitting the full tarsnap archive name into
        the creation time, retention, and ohsnap name"""
        self.full_name = full_name
        self.prefix, self.time, self.retention, self.name = full_name.split(':', 3)
        self.time = int(self.time)

    def time_string(self):
        """Return a human readable time string from the internal Unix style 
        time"""
        return time.strftime("%b %d %Y %H:%M:%S", 
            time.localtime(float(self.time)))
    
    def __repr__(self):
        return self.full_name

    def __str__(self):
        return self.full_name

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

