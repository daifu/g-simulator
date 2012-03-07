from nose.tools import *
from pygnutella.servent import Servent, FileInfo

def setup_func():
    """docstring for test_servent"""
    global servent
    servent = Servent(0)
    assert_equal(servent.files, [])

@with_setup(setup_func)
def test_check_file():    
    servent.set_files([FileInfo(1,"first file", 600),  FileInfo(2,"second file", 2500) , FileInfo(3, "third file", 5000)])
    assert_equal(servent.check_file(1), True)
    assert_equal(servent.check_file(200), False)

