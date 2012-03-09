from nose.tools import *
from pygnutella.servent import BasicServent, FileInfo
from pygnutella.message import Message
from pygnutella.messagebody import PingBody, PongBody

class TestServent(BasicServent):
    def on_connect(self, connection_handler):
        pass

class StoreServent(BasicServent):
    def on_receive(self, connection_handler, message):
        pass

def setup_func():
    """docstring for test_servent"""
    global servent1, servent2
    servent1 = TestServent()
    servent2 = StoreServent()
    assert_equal(servent.files, [])

@with_setup(setup_func)
def test_check_file():    
    servent.set_files([FileInfo(1,"first file", 600),  FileInfo(2,"second file", 2500) , FileInfo(3, "third file", 5000)])
    assert_equal(servent.check_file(1), True)
    assert_equal(servent.check_file(200), False)

def test_servent():
    asyncore.loop(timeout=1, count=5)  
    pass