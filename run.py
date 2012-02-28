from pygnutella.reactor import Reactor
import logging
import sys

def connector(connection_handler):
    print "connecting %s", connection_handler.socket.getsockname()
    
def acceptor():
    return True

def disconnector(connection_handler):
    print "disconnected"

def error(connection_handler, errno):
    print "error connection_handler = %s errno = %s", connection_handler.socket.getsockname(), errno

def receiver(connection_handler, message):
    print "receiving connection_handler = ", connection_handler.socket.getsockname()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')                        
    reactor = Reactor()
    reactor.install_handlers(acceptor, connector, receiver, disconnector, error)
    if len(sys.argv) > 2:
        reactor.make_outgoing_connection((sys.argv[1], int(sys.argv[2])))
    reactor.run()