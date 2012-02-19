from nose.tools import *
from pygnutella.message import Message

def test_message():
    # Test the default init
    msg = Message()
    assert_equal(msg.ttl, 7)
    assert_equal(msg.hops, 0)
    assert_equal(msg.body, None)
    assert_equal(msg.payload_length, 0)
    assert_equal(msg.payload_descriptor, None)
