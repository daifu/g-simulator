from pygnutella.servent import BasicServent, FileInfo
from pygnutella.message import create_message
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.scheduler import loop as scheduler_loop, close_all
from copy import deepcopy
from pygnutella.utils import dotted_quad_to_num
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
        self.cache = []
        BasicServent.__init__(self)

    def on_connect(self, connection_handler):
        ping_message = create_message(GnutellaBodyId.PING)
        self.send_message(ping_message, connection_handler)
        return

    def on_receive(self, connection_handler, message):
        self.log('QueryServent on_receive(): %s', message.body)
        # Check if message has ip attribute, which either are PONG, QUERYHIT,
        # and PUSH
        if hasattr(message.body, 'ip'):
            # Save the connection handler
            neighbor_ip = message.body.ip
            neighbor_port = message.body.port
            if (neighbor_ip, neighbor_port) not in self.neighbors:
                self.neighbors[(neighbor_ip, neighbor_port)] =\
                                                        connection_handler
        if message.payload_descriptor is GnutellaBodyId.QUERYHIT:
            # TODO: Save the path
            self.save_cache()
            # Start downloading
            self.log("Downloaded")
        BasicServent.on_receive(self, connection_handler, message)

    def flood(self, search_criteria):
        self.log('QueryServent flood(): %s', search_criteria)
        self.log('QueryServent neighbors: %s', self.neighbors)
        #Send message to all its neighbors
        query_message = create_message(GnutellaBodyId.QUERY,
                                        min_speed=10,
                                        search_criteria=search_criteria)
        for key in self.neighbors:
            self.send_message(query_message, self.neighbors[key])

    def save_cache(self):
        pass

class QueryHitServent(BasicServent):
    def __init__(self):
        self.neighbors = {}
        BasicServent.__init__(self)

    def on_receive(self, connection_handler, message):
        self.log('QueryHitServent on_receive(): %s', message.body)
        if hasattr(message.body, 'ip'):
            neighbor_ip = message.body.ip
            neighbor_port = message.body.port
            if (neighbor_ip, neighbor_port) not in self.neighbors:
                self.neighbors[(neighbor_ip, neighbor_port)] = connection_handler
        # Search throught its files if the message is QUERY
        if message.payload_descriptor is GnutellaBodyId.QUERY:
            match = self.search(message.body.search_criteria)
            if match:
                # Send query hit message back.
                # Construct queryhit message
                ip, port = self.reactor.address
                result_set = []
                for result in match:
                    result_set.append(result.get_result_set())
                num_of_hits = len(result_set)
                ip = dotted_quad_to_num(ip)
                query_hit_message = create_message(GnutellaBodyId.QUERYHIT,
                                                   num_of_hits=num_of_hits,
                                                   ip=ip,
                                                   port=int(port),
                                                   speed=100,
                                                   result_set=result_set,
                                                   servent_id=self.id)
                self.send_message(query_hit_message, connection_handler)
            else:
                self.log("Query Not Found!")
        BasicServent.on_receive(self, connection_handler, message)

def main():
    query_servent = QueryServent()
    query_hit_servent = QueryHitServent()
    query_hit_servent.set_files([FileInfo(1,"first file", 600),
                                 FileInfo(2,"second file", 2500) ,
                                 FileInfo(3, "third file", 5000)])
    query_hit_servent.reactor.gnutella_connect(query_servent.reactor.address)
    try:
        scheduler_loop(timeout=1,count=10)
    finally:
        query_servent.flood('first file')
        scheduler_loop(timeout=1,count=10)
        close_all()


if __name__ == '__main__':
    main()
