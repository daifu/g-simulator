from nose.tools import *
from message import Message

def test_message():
   msg = Message()
   assert_equal(msg.ttl, 7)
   assert_equal(msg.hops, 0)
   assert_equal(msg.body, None)
