from nose.tools import *
from pygnutella.servent import Servent


def setup_func():
    """docstring for test_servent"""
    servent = Servent('127.0.0.1', 9999)
    assert_equal(servent.ip, '127.0.0.1')
    assert_equal(servent.port, 9999)
    assert_equal(servent.files, [])

@with_setup(setup_func)

def test_check_file():
    servent.set_file([1,2,3])
    assert_equal(servent.check_file(1), True)
    assert_equal(servent.check_file(4), False)
