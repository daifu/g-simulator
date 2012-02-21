from nose.tools import *
from pygnutella.servent import Servent

def test_servent():
    """docstring for test_servent"""
    servent = Servent('', 5000)
    assert_equal(servent.ip, '')
    assert_equal(servent.port, 5000)
    assert_equal(servent.files, [])
