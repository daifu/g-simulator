from pygnutella.servent import Servent
from pygnutella.scheduler import loop as scheduler_loop, close_all
import logging

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