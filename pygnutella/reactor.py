import asyncore
import logging
import socket
import utils
from handshake import HandShakeOutContext, DownloadOutContext, ProbeContext

class Reactor:
    """
        Reactor is socket management class using Reactor Design Pattern
        User should not make more than one instance of Reactor.
        This will be enforce in the future by using Singleton Design Pattern
        
        3 Steps to use the class:
        
        1. Initialization:
        reactor = Reactor()
        reactor.install_handlers(acceptor, connector, receiver, disconnector, error)
        
        Handlers API and associated event and explainations
        + acceptor():
            call during handshake to ask Servant if they want to accept a gnutella connection
            sent during handshake. return True for accepting
        + connector(connection_handler): 
            call either after accepted an incoming connection or after successfully establish an outgoing connection i.e. 
            performance handshake successfully
        + receiver(connection_handler, message): 
            call when you receive a message which is defined by message.deserialize()
        + disconnector(connection_handler): 
            call AFTER connection is closed
        + downloader(event_id, connection_handler):
            call when there is a problem with a download connection
        
        2. Event Loop:
        reactor.run()
        
        3. Event occurs
        inside a event handler, send a message to connection corresponding to peer_id
        reactor.send(peer_id, message)
        
        OR
        reactor.make_outgoing_connection(address)
        + address is a tuple of (addr, port)        
    """
    
    def __init__(self, servent, port = 0):
        self._logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))        
        self.servent = servent
        self.channels = []
        self.server_handler = ServerHandler(reactor = self, port = port)        
        return
        
    def broadcast_except_for(self, handler, message):
        self._logger.debug("broadcast_except_for() -> %s", message.serialize())
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
        self._logger.debug("gnutella_connect() -> %s", address)
        try:
            ConnectionHandler(reactor = self, context_class = HandShakeOutContext, address = address)
        except:
            return False 
        return True
    
    def download_connect(self, address, remote_file_index, remote_file_name, local_file_name):
        self._logger.debug("gnutella_connect() -> %s", address)
        try:
            ConnectionHandler(reactor = self, 
                              context_class = DownloadOutContext, 
                              context_data = (remote_file_index, remote_file_name, local_file_name), 
                              address = address)
        except:
            return False 
        return True
    

class ServerHandler(asyncore.dispatcher):
    """
        This is the ServerHandler which is to handle incoming connections.        
    """
    def __init__(self, reactor, port):       
        self.reactor = reactor
        self._logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1
        self.bind((socket.gethostname(), port))
        # get socket address for future use
        self.reactor.ip, self.reactor.port = self.socket.getsockname()
        self.reactor.ip = utils.dotted_quad_to_num(self.reactor.ip)        
        self._logger.debug('ServerHandler binding to %s', self.socket.getsockname())
        # listening for incoming connection
        self.listen(5)
        return
    
    def handle_accept(self):
        sock, address = self.accept()
        self._logger.debug('handle_accept() -> %s', address)
        ConnectionHandler(reactor = self.reactor, context_class = ProbeContext, sock=sock)
        return
    
    def handle_close(self):
        self._logger.debug('handle_close()')
        self.close()
        self.reactor.server_handler = None     
        return
    
class ConnectionHandler(asyncore.dispatcher):
    """
        This is the handler for connection either incoming or outgoing.
        
        If outgoing, user simply creates handler and call
        handler.create_socket(address)
        
        If incoming, user simply create handler and call
        sock.setblocking(0)
        handler.set_socket(sock = sock)
    """    
    def __init__(self, reactor, context_class, 
                 context_data = None, address = None, sock = None, 
                 chunk_size=512, close_when_done = False):        
        self._logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        self._data_to_write = ''
        self.received_data = ''
        self.reactor = reactor
        self.chunk_size = chunk_size
        self._close_when_done = close_when_done                               
        if address:           
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self._logger.debug('connecting to %s', address)
            self.connect(address)
        elif sock:            
            asyncore.dispatcher.__init__(self, sock=sock)
        else:
            raise ValueError
        self.context = context_class(self, context_data)                                     
        return
        
    def write(self, data):
        self._data_to_write += data
        return
            
    def writable(self):        
        response = bool(self._data_to_write)
        self._logger.debug('writable() -> %s', response)
        return response
        
    def handle_close(self):
        self._logger.debug('handle_close()')        
        self.close()
        self.context.on_close()       
        return
    
    def handle_read(self):
        self.received_data += self.recv(self.chunk_size)
        self.context.on_read()
        return
    
    def handle_write(self):
        """
            Write as much as possible
        """        
        self._logger.debug('handle_write()')
        sent = self.send(self._data_to_write)        
        self._data_to_write = self._data_to_write[sent:]
        # check flag: close_after_last_write
        if self._close_when_done and not bool(self._data_to_write):
            self.handle_close()
        return
    
    def close_when_done(self):
        self._close_when_done = True
