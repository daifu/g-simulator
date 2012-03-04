import asyncore
import logging
import socket
import utils
from handshake import HandShakeOutContext, HandShakeInContext
from utils import print_hex

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
        
        2. Event Loop:
        reactor.run()
        
        3. Event occurs
        inside a event handler, send a message to connection corresponding to peer_id
        reactor.send(peer_id, message)
        
        OR
        reactor.make_outgoing_connection(address)
        + address is a tuple of (addr, port)        
    """
    
    def __init__(self, port = 0):
        self.logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))        
        self.connector = None
        self.disconnector = None
        self.error = None
        self.receiver = None
        self.acceptor = None
        self.channels = []
        handler = ServerHandler(reactor = self, port = port)
        self.add_channel(handler)
        return
    
    def send(self, handler, message):
        self.logger.debug("send() -> %s", message.serialize())        
        handler.send_message(message)
        return
    
    def broadcast_except_for(self, handler, message):
        self.logger.debug("broadcast_except_for() -> %s", message.serialize())
        for connection_handler in self.channels:
            if not connection_handler == handler:
                connection_handler.send_message(message)
        return
    
    def add_channel(self, handler):     
        self.channels.append(handler)
        return
    
    def remove_channel(self, handler):      
        try:                
            self.channels.remove(handler)
        except ValueError:
            pass        
    
    def install_handlers(self, acceptor, connector, receiver, disconnector):
        self.logger.debug("install_handlers()")
        assert callable(acceptor)
        assert callable(connector)
        assert callable(receiver)
        assert callable(disconnector)
        self.acceptor = acceptor
        self.connector = connector
        self.receiver = receiver
        self.disconnector = disconnector
        return
    
    def make_outgoing_connection(self, address):
        self.logger.debug("make_outgoing_connection() -> %s", address)
        ConnectionHandler(reactor = self, address = address)
        return
    
    def run(self, timeout = 30):
        if not (self.acceptor and self.connector and self.disconnector and self.receiver):
            raise ValueError
        self.logger.debug("run(%s)", timeout)
        asyncore.loop(timeout);
        return

class ServerHandler(asyncore.dispatcher):
    """
        This is the ServerHandler which is to handle incoming connections.        
    """
    def __init__(self, reactor, port):       
        self.reactor = reactor
        self.logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1
        self.bind((socket.gethostname(), port))
        # get socket address for future use
        self.reactor.ip, self.reactor.port = self.socket.getsockname()
        self.reactor.ip = utils.dotted_quad_to_num(self.reactor.ip)        
        self.logger.debug('ServerHandler binding to %s', self.socket.getsockname())
        # listening for incoming connection
        self.listen(5)
        return
    
    def handle_accept(self):
        sock, address = self.accept()
        self.logger.debug('handle_accept() -> %s', address)
        ConnectionHandler(reactor = self.reactor, sock=sock)
        return
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        self.reactor.disconnector(self)
        self.reactor.remove_channel(self)        
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
    def __init__(self, reactor, address = None, sock = None, chunk_size=512):        
        self.logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        self.data_to_write = ''
        self.received_data = ''
        self.reactor = reactor
        self.chunk_size = chunk_size                                 
        if address:
            self.context = HandShakeOutContext(self)              
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.debug('connecting to %s', address)
            self.connect(address)
        elif sock:
            self.context = HandShakeInContext(self)            
            asyncore.dispatcher.__init__(self, sock=sock)
        else:
            raise ValueError                                        
        return
    
    def send_message(self, message):
        self.logger.debug('send_message()')
        print_hex(message.serialize())
        self.write(message.serialize())
        return
    
    def write(self, data):
        self.data_to_write += data
        return
            
    def writable(self):        
        response = bool(self.data_to_write)
        self.logger.debug('writable() -> %s', response)
        return response
        
    def handle_close(self):
        self.logger.debug('handle_close()')        
        self.close()
        self.reactor.disconnector(self)
        self.reactor.remove_channel(self)        
        return
    
    def handle_read(self):
        self.received_data += self.recv(self.chunk_size)
        self.context = self.context.on_read()
        return
    
    def handle_write(self):
        """
            Write as much as possible
        """        
        self.logger.debug('handle_write()')
        sent = self.send(self.data_to_write)        
        self.data_to_write = self.data_to_write[sent:]
        return
    
class DownloadHandler(asyncore.dispatcher):
    def __init__(self):
        pass