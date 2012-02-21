from nose.tools import *
from pygnutella.messagebody import *
from pygnutella.message import Message

def test_PingBody():
    message = Message()
    ping = PingBody(message)
    assert_equal(ping.message, message)
    assert_equal(ping.get_length(), 0)
    assert_equal(ping.serialize(), b'')
    
def test_PongBody():
    message = Message()
    pong = PongBody(message)
    assert_equal(pong.message, message)

def test_PushBody():
    message = Message()
    push = PushBody(message)
    assert_equal(push.message, message)
    
def test_QueryBody():
    message = Message()
    query = QueryBody(message)
    assert_equal(query.message, message)

def test_QueryHitBody():
    message = Message()
    query_hit = QueryHitBody(message)
    assert_equal(query_hit.message, message)
