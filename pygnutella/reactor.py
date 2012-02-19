import asyncore
import logging
import socket

class Reactor:
    def __init__(self, address):
        self.logger = logging.getLogger(__name__)
        self.acceptor = None
        self.disconnector = None
        self.error = None
        self.receiver = None
        return
    
    def install_handlers(self, acceptor, receiver, disconnector, error):
        self.acceptor = acceptor
        self.receiver = receiver
        self.disconnector = disconnector
        self.error = error;
        return
    
    def make_outgoing_connection(self):
        # TODO implement this method
        pass
    
    def run(self):
        if not (self.acceptor and self.disconnector and self.receiver and self.error):
            # TODO throw exception here
            return
        asyncore.loop();
        return

class BasicServer(asyncore.dispatcher):
    def __init__(self, reactor, address):
        if reactor == None:
            raise ValueError        
        self.reactor = reactor
        self.logger = logging.getLogger(__name__)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsocketname()
        self.logger.debug('binding to %s', self.address)
        self.listen(5)
        return
    
    def handle_accept(self):
        peer_info = self.accept()
        self.logger.debug('handle_accept() -> %s', peer_info)        
        return;
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        return
    
class IConnectionHandler():
    def __init__(self, reactor):
        self.reactor = reactor
        return
    
    def handle_connect(self):
        pass
    
    def handle_close(self):
        pass
    
    def handle_read(self):
        pass
    
    def handle_write(self):
        pass
    
    def handle_error(self):
        pass
    
class IncomingConnectionHandler(IConnectionHandler, asyncore.dispatcher):
    def __init__(self, reactor):
        IConnectionHandler.__init__(self, reactor)
        return
    
class OutgoingConnectionHandler(IConnectionHandler, asyncore.dispatcher):
    def __init__(self, reactor):
        IConnectionHandler.__init__(self, reactor)
        return
        