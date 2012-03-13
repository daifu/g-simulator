from ..message import create_message
from ..messagebody import GnutellaBodyId
from copy import deepcopy
from ..utils import dotted_quad_to_num
from ..servent import BasicServent
import logging

class CacheServent(BasicServent):
    """
    It cached only for the QueryHit servents.
    When it meets the same search_criteria, then send_message to the previous
    query hit servents.
    """

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
            # if this message is mine
            if message.message_id in self.ignore:
                # Start downloading
                self.log("Downloaded")

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
                                                   message_id=message.message_id,
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

    def query_flood(self, search_criteria):
        #Send message to all its neighbors
        query_message = create_message(GnutellaBodyId.QUERY,
                                        min_speed=10,
                                        search_criteria=search_criteria)
        for key in self.neighbors:
            self.send_message(query_message, self.neighbors[key])
        # BasicServent.flood(self, None, query_message)

    def save_cache(self):
        pass
