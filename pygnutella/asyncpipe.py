from asyncore import file_dispatcher
from sys import stderr
from errno import EPIPE, EBADF
from traceback import print_exc

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
    
    def handle_write(self):
        # writable as muchas possible
        sent = self.send(self._data_to_write)
        self._data_to_write = self._data_to_write[sent:]
        if not bool(self._data_to_write) and self._close_when_done:
            self.handle_close()
    
class OutPipeDispatcher(PipeDispatcher):
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