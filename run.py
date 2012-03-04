from pygnutella.servent import Servent
from pygnutella.message import Message
from pygnutella.messagebody import PingBody
from pygnutella.utils import print_hex
from pygnutella.scheduler import loop as scheduler_loop, CallEvery
import logging, sys


def connector(connection_handler):
    print "connecting %s", connection_handler.socket.getsockname()
    msg = Message('somemsgid')
    PingBody(msg)
    connection_handler.send_message(msg)
    
def acceptor():
    return True

def disconnector(connection_handler):
    print "disconnected"

def receiver(connection_handler, message):
    print_hex(message.serialize())
    return

def timeout():
    print "hello world"

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')                        
    servent = Servent()
    # call back every 5.1 seconds
    CallEvery(5.1, timeout) 
    if len(sys.argv) > 2:
        servent.reactor.gnutella_connect((sys.argv[1], int(sys.argv[2])))
    scheduler_loop()