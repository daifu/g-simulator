from pygnutella.reactor import Reactor
import logging
import sys

def connector(peer_id):
    print "connecting %s", peer_id
    
def acceptor():
    return True

def disconnector(peer_id):
    print "disconnected %s", peer_id

def error(peer_id, errno):
    print "error peer_id = %s errno = %s", peer_id, errno

def receiver(peer_id , message):
    print "receiving peer_id = ", peer_id

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-6s %(name)s: %(message)s')                        
    reactor = Reactor(('localhost', 0)) # let the kernel give us a port
    reactor.install_handlers(acceptor, connector, receiver, disconnector, error)
    if len(sys.argv) > 1:
        reactor.make_outgoing_connection(('localhost', int(sys.argv[1])))
    reactor.run()