from nose.tools import *
from pygnutella.handshake import *

def test_Gnutella4Handshake_init():
    handler = {}
    global gnutella
    gnutella = Gnutella4Handshake(handler)
    assert_equal(gnutella.handler, {})

@with_setup(test_Gnutella4Handshake_init)

def test_onIncoming():
    gnutella.onIncoming
    #assert_equal(g_welcome, 'something')
