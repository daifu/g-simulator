from nose.tools import *
from pygnutella.reactor import Reactor

def setup_func():
    global reactor
    address = ('127.0.0.1', 9990)
    reactor = Reactor(address)
    assert_not_equal(reactor.channels, [])

@with_setup(setup_func)

def test_init():
    #TODO: do more tests.
    pass
