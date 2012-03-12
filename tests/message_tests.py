from nose.tools import *
from pygnutella.message import Message, create_message
from pygnutella.messagebody import PingBody, GnutellaBodyId

def test_message():
    # Test the default init
    msg = Message()    
    assert_equal(msg.ttl, 7)
    assert_equal(msg.hops, 0)
    assert_equal(msg.payload_descriptor, None)
    PingBody(msg)

    # test short cut
    msg = create_message(GnutellaBodyId.PING)
    assert_equal(msg.ttl, 7)
    assert_equal(msg.hops, 0)
    assert_equal(msg.payload_descriptor, GnutellaBodyId.PING)


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

def test_create_query_message():
    msg_id = 'something'
    ttl = 7
    msg = create_message(GnutellaBodyId.QUERY,
                         msg_id, ttl,
                         min_speed=10,
                         search_criteria="file")

    assert_equal(msg.ttl, ttl)
    assert_equal(msg.body.search_criteria, "file")
    assert_equal(msg.body.min_speed, 10)

    # test serialize()
    expected_msg =\
    'something\x00\x00\x00\x00\x00\x00\x00\x80\x07\x00\x00\x00\x00\x06\nfile\x00'
    assert_equal(msg.serialize(), expected_msg)
