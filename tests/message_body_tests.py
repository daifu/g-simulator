from nose.tools import *
from pygnutella.messagebody import *

def test_PingBody():
   ping = PingBody('')
   assert_equal(ping.message, '')
   #try out the default set method
   ping.message = 'none'
   assert_equal(ping.message, 'none')

def test_PongBody():
   #TODO: test pong body
