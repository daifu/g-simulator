#!/usr/bin/env python

#make sure this file is executable
#chmod 755 setup.py

print "Checking all the packages"
try:
    import logging
    import asyncore
    import socket
    import uuid
    import struct
    from subprocess import call

    print "All system required system package installed."
except ImportError, e:
    import sys
    if sys.version_info <= (2, 7,):
        print "Please upgrade your python to at least 2.7"
        print "Python upgrade page: http://www.python.org/download/releases/"
    else:
        print e

print "Checking nose(Testing library)"
try:
    import nose
    print "Run all unit tests"
    call('nosetests')
except Exception, e:
    print "No nose module, start installing nose"
    call('sudo easy_install nose', shell=True)
    print "Run all unit tests"
    call('nosetests')

