from nose.tools import *
import os
from pygnutella.asyncpipe import *
import asyncore

class TestOutputPipe(LogOutputPipeDispatcher):
    def __init__(self, fh):
        LogOutputPipeDispatcher.__init__(self, fh)
        self.queue = []
    
    def handle_log(self, msg):
        self.queue.append(msg)
        
def test_pipes():
    rp, wp = os.pipe()
    in_pipe = LogInputPipeDispatcher(os.fdopen(wp, 'wb'), 'Test')
    out_pipe = TestOutputPipe(os.fdopen(rp, 'rb'))
    in_pipe.log('hello world')
    in_pipe.log('test this')
    in_pipe.log('last message')
    asyncore.loop(timeout=1, count=2)  
    assert_equals(out_pipe.queue[0], 'Test: hello world')
    assert_equals(out_pipe.queue[1], 'Test: test this')
    assert_equals(out_pipe.queue[2], 'Test: last message')
