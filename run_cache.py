from pygnutella.servent import BasicServent, FileInfo
from pygnutella.message import create_message
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.scheduler import loop as scheduler_loop, close_all
from copy import deepcopy
import logging

#TODO:
# 1. when receiving the PONG message, save its information with this format:
# neighbors = {(ip, port): connection_handler, ...}
# 2. try to send a query from query_servent to query_hit_servent
# 3. query_hit_servent response query_hit to the query_servent, and save the
# path to the cache
# 4. query_servent will start downloading.

class QueryServent(BasicServent):
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
        self.neighbors = {}
        BasicServent.__init__(self)

    def on_connect(self, connection_handler):
        ping_message = create_message(GnutellaBodyId.PING)
        self.send_message(ping_message, connection_handler)
        return

    def on_receive(self, connection_handler, message):
        self.log('QueryServent on_receive(): %s', message.body)
        if message.payload_descriptor is not GnutellaBodyId.PING:
            # Save the connection handler
            neighbor_ip = message.body.ip
            neighbor_port = message.body.port
            if (neighbor_ip, neighbor_port) not in self.neighbors:
                self.neighbors[(neighbor_ip, neighbor_port)] = connection_handler

        BasicServent.on_receive(self, connection_handler, message)

    def flood(self, search_criteria):
        self.log('QueryServent flood(): %s', message.body)
        #Send message to all its neighbors
        query_message = create_message(GnutellaBodyId.QUERY, None, 7,
                min_speed=10, search_criteria=search_criteria)
        for handler in self.neighbors:
            BasicServent.send_message(query_message, handler)

class QueryHitServent(BasicServent):
    def __init__(self):
        self.neighbors = {}
        BasicServent.__init__(self)

    def on_receive(self, connection_handler, message):
        self.log('QueryHitServent on_receive(): %s', message.body)
        if message.payload_descriptor is not GnutellaBodyId.PING:
            neighbor_ip = message.body.ip
            neighbor_port = message.body.port
            if (neighbor_ip, neighbor_port) not in self.neighbors:
                self.neighbors[(neighbor_ip, neighbor_port)] = connection_handler
        BasicServent.on_receive(self, connection_handler, message)

def main():
    query_servent = QueryServent()
    query_hit_servent = QueryHitServent()
    query_hit_servent.set_files([FileInfo(1,"first file", 600),
                                 FileInfo(2,"second file", 2500) ,
                                 FileInfo(3, "third file", 5000)])
    query_hit_servent.reactor.gnutella_connect(query_servent.reactor.address)
    # query_servent.flood('first file')
    try:
        scheduler_loop(timeout=1,count=10)
    finally:
        close_all()


if __name__ == '__main__':
    main()
