from pygnutella.servent import Servent
from pygnutella.message import Message
from pygnutella.messagebody import PingBody
from pygnutella.utils import print_hex
from pygnutella.scheduler import loop as scheduler_loop, close_all
import logging


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
    servent1 = Servent()
    servent2 = Servent()
    servent2.reactor.gnutella_connect((servent1.reactor.address))
    try:
        scheduler_loop()
    finally:
        # clean up
        close_all()