from pygnutella.servent import BasicServent
from pygnutella.scheduler import loop as scheduler_loop, close_all
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')                     
    servent1 = BasicServent()
    servent2 = BasicServent()
    servent2.reactor.gnutella_connect((servent1.reactor.address))
    try:
        scheduler_loop(timeout=1, count=10)
    except:
        pass
    finally:
        # clean up
        close_all()