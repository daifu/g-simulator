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
    #TODO: test pong body
