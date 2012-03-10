import asyncore
import socket
import utils
from bootstrap import BootstrapOutHandler

class Reactor:
    """
        Reactor is socket management class using Reactor Design Pattern
        User should not make more than one instance of Reactor.
        
        3 Steps to use the class:
        
        1. Initialization:
        reactor = Reactor(servent)
                        
        2. Event Loop:
        asyncore.loop()
        
        OR
        
        scheduler.loop()        
    """
    
    def __init__(self, servent, port = 0):
        self.servent = servent
        self.channels = []
        self.server_handler = GnutellaServer(reactor = self, port = port)        
        return
        
    def broadcast_except_for(self, handler, message):
        packet = message.serialize()
        for connection_handler in self.channels:
            if not connection_handler == handler:
                connection_handler.write(packet)
        return
    
    def add_channel(self, handler):     
        self.channels.append(handler)
        return
    
    def remove_channel(self, handler):      
        try:                
            self.channels.remove(handler)
        except ValueError:
            pass        
        
    def gnutella_connect(self, address):
        self.servent.log("gnutella_connect() -> %s %s" % address)
        try:
            GnutellaClientHandler(self, address)
        except socket.error:
            self.servent.log("failed to connect")
            return False 
        return True
    
    def download_connect(self, address, remote_file_index, remote_file_name, local_file_name):
        self.servent.log("download_connect() -> %s %s" % address)
        try:
            DownloadClientHandler(self, 
                                  remote_file_index, 
                                  remote_file_name, 
                                  local_file_name, address)
        except socket.error:
            self.servent.log("failed to connect")
            return False 
        return True
    
    def bootstrap_connect(self, address):
        self.servent.log('bootstrap_connect() -> %s %s' % address)
        try:
            self.bootstrap_handler = BootstrapOutHandler(node_address = self.address, 
                                                         bootstrap_address = address, 
                                                         servent = self.servent)
        except socket.error:
            self.servent.log("failed to connect")
            return False
        return True

class GnutellaServer(asyncore.dispatcher):
    """
        This is the GnutellaServer which is to handle incoming connections.        
    """
    def __init__(self, reactor, port):       
        self.reactor = reactor
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1
        self.bind((socket.gethostname(), port))
        # get socket address for future use
        self.reactor.address = self.socket.getsockname()
        self.reactor.ip = utils.dotted_quad_to_num(self.reactor.address[0])
        self.reactor.port = self.reactor.address[1]        
        self.reactor.servent.log('bind to %s %s' % self.reactor.address)
        # listening for incoming connection
        self.listen(5)
        return
    
    def handle_accept(self):
        sock, _ = self.accept()
        self.reactor.servent.log('tcp connection established')
        ServerHandler(self.reactor, sock=sock)
        return
    
    def handle_close(self):
        self.close()
        self.reactor.server_handler = None     
        return
    
class ConnectionHandler(asyncore.dispatcher):
    """
        This is a generic handler for connection either incoming or outgoing.
        
        Derive this class hook process_read()
    """    
    def __init__(self, reactor, chunk_size=512, close_when_done = False):        
        self._data_to_write = ''
        self.received_data = ''
        self.process_read = None
        self.reactor = reactor
        self.chunk_size = chunk_size
        self._close_when_done = close_when_done
        asyncore.dispatcher.__init__(self)
        return
        
    def write(self, data):
        self._data_to_write += data
        return
                
    def writable(self):            
        response = bool(self._data_to_write)
        return response
        
    def handle_close(self):
        self.reactor.servent.log('handle_close()')       
        self.close()
        self._context.on_close()       
        return
    
    def handle_read(self):
        #self.reactor.servent.log("handle_read() -> %s", self._context)
        self.received_data += self.recv(self.chunk_size)
        if callable(self.process_read):
            self.process_read()
        else:
            self.reactor.servent.log("process_read() is not callable")
        return
    
    def handle_write(self):
        """
            Write as much as possible
        """
        sent = self.send(self._data_to_write)
        #self.reactor.servent.log("handle_write() -> to: %s buffer: %d sent: %d", self.socket.getpeername(), len(self._data_to_write), sent)        
        self._data_to_write = self._data_to_write[sent:]
        # check flag: close_after_last_write
        if self._close_when_done and not self.writable():
            self.reactor.servent.log("close_when_done()")
            self.handle_close()
        return
    
    def close_when_done(self):
        self._close_when_done = True

class ServerHandler(ConnectionHandler):
    def __init__(self, reactor, sock):
        ConnectionHandler.__init__(self, reactor)
        sock.setblocking(False)
        self.set_socket(sock)
        self.process_read = self._probe
        
    def _probe(self):
        pass
    
    def _handshake(self):
        pass
            
    def _download(self):
        pass
    
    def _gnutella(self):
        pass
    
    def handle_close(self):
        ConnectionHandler.handle_close(self)
    
class GnutellaClientHandler(ConnectionHandler):
    def __init__(self, reactor, address):
        ConnectionHandler.__init__(self, reactor)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address)
        self.process_read = self._handshake
        
    def _handshake(self):
        pass
    
    def _gnutella(self):
        pass
    
    def handle_close(self):
        ConnectionHandler.handle_close(self)    
    
class DownloadClientHandler(ConnectionHandler):
    def __init__(self, reactor, address, remote_file_index, remote_file_name, local_file_name):
        ConnectionHandler.__init__(self, reactor)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address)
        self.process_read = self._download
        self._remote_file_index = remote_file_index
        self._remote_file_name = remote_file_name
        self._local_file_name = local_file_name
        
    def _download(self):
        pass

    def handle_close(self):
        ConnectionHandler.handle_close(self)