from asyncore import file_dispatcher, loop
from sys import stderr
from errno import EPIPE, EBADF
from traceback import print_exc
import os

class PipeDispatcher(file_dispatcher):
    def __init__(self, fh, ignore_broken_pipe=False):
        if ignore_broken_pipe:
            self.__ignore_errno = [EPIPE, EBADF]
        else:
            self.__ignore_errno = []
        file_dispatcher.__init__(self, fh)
    
    def close(self):
        if self.connected:
            try:
                file_dispatcher.close(self)
            except OSError, oe:
                if oe.errno not in self.__ignore_errno:
                    print_exc(file=stderr)
            finally:
                self.connected = False
                
    def readable(self):
        return self.connected
    
    def writable(self):
        return self.connected
    
    def send(self, data):
        if self.connected:
            try:
                return file_dispatcher.send(self, data)
            except OSError, oe:
                if oe.errno in self.__ignore_errno: 
                    self.handle_close()
                else:
                    self.handle_expt()
    
    def recv(self, buffer_size):
        if self.connected:
            try:
                return file_dispatcher.recv(self, buffer_size)
            except OSError, oe:
                if oe.errno in self.__ignore_errno: 
                    self.handle_close()
                else:
                    self.handle_expt()
        return ''
    
    def handle_close(self):
        self.close()
        
    def handle_expt(self):
        print_exc(file=stderr)
        self.handle_close()                
        
class InputPipeDispatcher(PipeDispatcher):
    def __init__(self, fh, close_when_done=False):
        PipeDispatcher.__init__(self, fh)
        self._close_when_done = close_when_done
        self._data_to_write = ''
        
    def readable(self):
        return False
    
    def writable(self):
        return PipeDispatcher.writable(self) and bool(self._data_to_write)
    
    def write(self, data):
        self._data_to_write += data
    
    def handle_write(self):
        # writable as muchas possible
        sent = self.send(self._data_to_write)
        self._data_to_write = self._data_to_write[sent:]
        if not bool(self._data_to_write) and self._close_when_done:
            self.handle_close()
            
    def close_when_done(self):
        self._close_when_done = True
    
class OutputPipeDispatcher(PipeDispatcher):
    def __init__(self, fh, chunk_size=512):
        PipeDispatcher.__init__(self, fh)
        self._received_data = ''
        self._chunk_size = chunk_size
    
    def readable(self):
        return True
    
    def writable(self):
        return False
    
    def handle_read(self):
        self._received_data += self.recv(self._chunk_size)
        
class LogInputPipeDispatcher(InputPipeDispatcher):
    def __init__(self, fh, name, terminator='\n'):
        self._name = name+": "
        InputPipeDispatcher.__init__(self, fh)
        self._terminator = terminator
        
    def log(self, msg, *args, **kwargs):
        self.write(self._name)
        self.write(msg.format(*args, **kwargs))
        self.write(self._terminator)
        
    def set_terminator(self, terminator):
        self._terminator = terminator
        
class LogOutputPipeDispatcher(OutputPipeDispatcher):
    def __init__(self, fh, terminator='\n'):
        OutputPipeDispatcher.__init__(self, fh)
        self._terminator = terminator
        self._len_t = len(terminator)

    def set_terminator(self, terminator):
        self._terminator = terminator
        self._len_t = len(terminator)

    def handle_read(self):
        OutputPipeDispatcher.handle_read(self)
        if self._terminator in self._received_data:
            idx = self._received_data.find(self._terminator)
            self.handle_log(self._received_data[:idx])
            self._received_data = self._received_data[idx+self._len_t:]
                        
    def handle_log(self, msg):
        # output back to the terminal
        print msg        

def __example_pipe():
    rp, wp = os.pipe()
    InputPipeDispatcher(os.fdopen(wp, 'wb'))
    OutputPipeDispatcher(os.fdopen(rp, 'rb'))
    loop()    