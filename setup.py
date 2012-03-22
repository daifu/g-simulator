#!/usr/bin/env python

#make sure this file is executable
#chmod 755 setup.py
import sys
from subprocess import call


def check():
    """Check whether the system has all the package or not"""
    print "Checking all the packages"
    try:
        import logging
        import asyncore
        import socket
        import uuid
        import struct
        import asynchat
        import multiprocessing
        import numpy
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
        call('nosetests', shell=True)
    except Exception, e:
        print "No nose module, please installing nose: "
        print "sudo pip install nose OR sudo easy_install nose"

def uninstall():
    """Uninstall the nose package"""
    print "Uninstalling nose pacakge, it might require admin permission."
    print "Running pip uninstall nose"
    try:
        re = call("pip uninstall nose", shell=True)
        if re == 0:
            print "Done!"
    except Exception, e:
        raise e

def main(argv):
    if len(argv) == 0:
        print "Missing arguments."
        print "Usage: python setup.py [check|uninstall]"
        return
    if argv[0] == "check":
        check()
    elif argv[0] == "uninstall":
        uninstall()
    else:
        print "Unknown arguments."
        print "Usage: python setup.py [check|uninstall]"
        return

if __name__ == "__main__":
    main(sys.argv[1:])
