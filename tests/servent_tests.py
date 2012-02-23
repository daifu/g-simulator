from nose.tools import *
from pygnutella.servent import Servent

class GnutellaBodyId:
    PING = 0x00
    PONG = 0x01
    QUERY = 0x80
    QUERYHIT = 0x81
    PUSH = 0x40

def setup_func():
    """docstring for test_servent"""
    global servent
    servent = Servent('127.0.0.1', 9999)
    assert_equal(servent.ip, '127.0.0.1')
    assert_equal(servent.port, 9999)
    assert_equal(servent.files, [])

@with_setup(setup_func)

def test_check_file():
    servent.set_files([1,2,3])
    assert_equal(servent.check_file(1), True)
    assert_equal(servent.check_file(4), False)

def test_create_message():
    # ping
    servent.create_message('abc', GnutellaBodyId.PING, '')
