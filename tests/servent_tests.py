from nose.tools import *
from pygnutella.servent import Servent

def test_servent():
    """docstring for test_servent"""
    servent = Servent('192.168.1.1', '5000')
    assert_equal(servent.ip, '192.168.1.1')
    assert_equal(servent.port, '5000')
    assert_equal(servent.files, [])
