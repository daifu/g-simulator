from nose.tools import *
from pygnutella.message import Message
from pygnutella.messagebody import PingBody

def test_message():
    # Test the default init
    msg = Message(message_id = '')    
    assert_equal(msg.ttl, 7)
    assert_equal(msg.hops, 0)
    assert_equal(msg.payload_length, None)
    assert_equal(msg.payload_descriptor, None)
    assert_not_equals(msg.message_id, None)
    PingBody(msg)
    
    # test serialization
    expected_message = msg.message_id + '\x00\x07\x00\x00\x00\x00\x00'
    ser = msg.serialize()
    assert_equal(ser, expected_message)
    
    # test deserialization
    new_message = Message()
    new_message.deserialize(expected_message)
    assert_equal(msg.ttl, 7)
    assert_equal(msg.hops, 0)
    assert_equal(msg.payload_length, 0)
    assert_equal(msg.payload_descriptor, 0)    
