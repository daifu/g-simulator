from nose.tools import *
from pygnutella.reactor import Reactor

def setup_func():
    global reactor
    reactor = Reactor()
    assert_equal(reactor.channels, [])

@with_setup(setup_func)

def test_init():
    #TODO: do more tests.
    pass
