from nose.tools import *
from pygnutella.messagebody import *

def test_PingBody():
   ping = PingBody('')
   assert_equal(ping.message, '')

def test_PongBody():
   pong = PongBody()
