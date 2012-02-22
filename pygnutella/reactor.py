import asyncore
import logging
import socket

class Reactor:
    """
        Reactor is socket management class using Reactor Design Pattern
        User should not make more than one instance of Reactor.
        This will be enforce in the future by using Singleton Design Pattern
        
        3 Steps to use the class:
        
        1. Initialization:
        reactor = Reactor()
        reactor.install_handlers(connector, receiver, disconnector, error)
        
        Handlers API and associated event and explainations
        + connector(peer_id): 
            call either after accepted an incoming connection or after successfully establish an outgoing connection
        + receiver(peer_id, message): 
            call when you receive a message which is defined by message.deserialize()
        + disconnector(peer_id): 
            call AFTER connection is closed
        + error(peer_id, errno): 
            call when an error raised
        + peer_id SHOULD NOT be used in anyway except to identify the connection
        
        2. Event Loop:
        reactor.run()
        
        3. Event occurs
        inside a event handler, send a message to connection corresponding to peer_id
        reactor.send(peer_id, message)
        
        OR
        reactor.make_outgoing_connection(address)
        + address is a tuple of (addr, port)
        
    """
    def __init__(self, address):
        self.logger = logging.getLogger(__name__)
        self.connector = None
        self.disconnector = None
        self.error = None
        self.receiver = None
        self.channels = {}
        handler = ServerHandler(self, address)
        self.add(handler.socket, handler)
        return
    
    def send(self, peer_id, message):
        self.logger.debug("send() -> %s", message)
        self.channels[peer_id].send_message(message)
        return
    
    def add(self, peer_id, handler):
        self.logger.debug("add() -> %s", peer_id)
        self[peer_id] = handler
        return
    
    def remove(self, peer_id):
        self.logger.debug("remove() -> %s", peer_id)
        del self.channels[peer_id]
    
    def install_handlers(self, connector, receiver, disconnector, error):
        self.logger.debug("install_handlers()")
        self.connector = connector
        self.receiver = receiver
        self.disconnector = disconnector
        self.error = error;
        return
    
    def make_outgoing_connection(self, address):
        self.logger.debug("make_outgoing_connection() -> %s", address)
        handler = ConnectionHandler(reactor = self)
        handler.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.add(handler.socket, handler)
        return
    
    def run(self):
        if not (self.acceptor and self.disconnector and self.receiver and self.error):
            raise ValueError
        asyncore.loop();
        return

class ServerHandler(asyncore.dispatcher):
    """
        This is the ServerHandler which is to handle incoming connections.        
    """
    def __init__(self, reactor, address):       
        self.reactor = reactor
        self.logger = logging.getLogger(__name__)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsocketname() # TODO: getsocketname() for self.socket
        self.address = self.socket.getsockname()
        self.logger.debug('ServerHandler binding to %s', self.address)
        self.listen(5)
        return
    
    def handle_accept(self):
        sock, address = self.accept()
        self.logger.debug('handle_accept() -> %s', address)
        handler = ConnectionHandler(reactor = self.reactor)
        sock.setblocking(0)
        handler.set_socket(sock = sock)
        self.reactor.add(sock, handler)
        self.reactor.connector(sock)                
        return
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        self.reactor.disconnector(self.socket)
        self.reactor.remove(self.socket)        
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
    def __init__(self, reactor, chunk_size=512):        
        self.logger = logging.getLogger(__name__)
        self.reactor = reactor
        self.chunk_size = chunk_size
        self.data_to_write = b''
        self.received_data = b''
        asyncore.dispatcher.__init__(self)
        return
    
    def send_message(self, message):
        self.logger.debug('send_message() -> %s', message)
        self.data_to_write += message.serialize()
        return
    
    def writable(self):
        response = bool(self.data_to_write)
        self.logger.debug('writable() -> %s', response)
        return response
    
    def handle_connect(self):
        self.logger.debug('handle_connect()')
        self.reactor.connector(self.socket) # FIXED THIS
        return
    
    def handle_close(self):
        self.logger.debug('handle_close()')        
        self.close()
        self.reactor.disconnector(self.socket)
        self.reactor.remove(self.socket)        
        return
    
    def handle_read(self):
        self.logger.debug('handle_read()')
        self.received_data += self.recv(self.chunk_size)
        # TODO: deserialize the receive_data
        return
    
    def handle_write(self):
        """
            Write as much as possible
        """        
        sent = self.send(self.data_to_write)
        self.logger.debug('handle_write() -> (%d) %s', sent, self.data_to_write[:sent])
        self.data_to_write = self.data_to_write[sent:]
        return
    
    def handle_error(self):
        self.logger.debug('handle_error()')
        # TODO: this too
        self.reactor.error(self.socket, 1)
        return        
