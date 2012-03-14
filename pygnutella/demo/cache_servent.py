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

    def __init__(self, bootstrap_address=None):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
        self.neighbors = {}
        self.cache = []
        BasicServent.__init__(self, bootstrap_address=bootstrap_address)

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
            self.save_cache(message)
            # if this message is mine
            if message.message_id in self.ignore:
                # Start downloading
                self.log("%s Downloaded file from %s", self.reactor.address
                                    , (message.body.ip, message.body.port))

        # Search throught its files if the message is QUERY
        if message.payload_descriptor is GnutellaBodyId.QUERY:
            match = self.search(message.body.search_criteria)
            if match:
                self.log("%s Found! Send Query Hit", self.reactor.address)
                self.response_query_hit(message, match, connection_handler, False)
                # terminate the process
                return
            else:
                self.log("%s Not Found! Search in Cache.", self.reactor.address)
                # search in cache
                cache_match = self.search_in_cache(message.body.search_criteria)
                if cache_match is not False:
                    # send the query hit message back to the requester
                    self.response_query_hit(message,
                                            cache_match,
                                            connection_handler,
                                            True)
                    # terminate the process
                    return
        BasicServent.on_receive(self, connection_handler, message)

    def response_query_hit(self, message, match, connection_handler, is_cache):
        # Send query hit message back.
        # Construct queryhit message
        if not is_cache:
            ip, port = self.reactor.address
            result_set = []
            result_set.append(match.get_result_set())
            servent_id = self.id
        else:
            ip, port = match['address']
            result_set = match['result_set']
            servent_id = match['servent_id']
        num_of_hits = len(result_set)
        ip = dotted_quad_to_num(ip)
        query_hit_message = create_message(GnutellaBodyId.QUERYHIT,
                                           message_id=message.message_id,
                                           num_of_hits=num_of_hits,
                                           ip=ip,
                                           port=int(port),
                                           speed=100,
                                           result_set=result_set,
                                           servent_id=servent_id)
        self.send_message(query_hit_message, connection_handler)

    def query_flood(self, search_criteria):
        self.log("%s sending QUERY message", self.reactor.address)
        result = self.search_in_cache(search_criteria)
        if result is not False:
            # download the file
            self.log("%s Download from %s", self.reactor.address
                                          , result['address'])
            return
        #Send message to all its neighbors
        query_message = create_message(GnutellaBodyId.QUERY,
                                        min_speed=10,
                                        search_criteria=search_criteria)
        for key in self.neighbors:
            self.send_message(query_message, self.neighbors[key])
        # BasicServent.flood(self, None, query_message)

    def save_cache(self, message):
        # if the message is not duplicated in the cache, save it
        is_duplicate = False
        for cache in self.cache:
            if message.body.result_set == cache['result_set']:
                is_duplicate = True
                break
        if is_duplicate:
            return False
        # save the message.body.result_set to cache
        self.log("%s save message!", self.reactor.address)
        cache = {
            'address': (str(message.body.ip), message.body.port),
            'result_set': message.body.result_set,
            'servent_id': message.body.servent_id,
        }
        self.cache.append(cache)
        self.log("%s has message: %s", self.reactor.address
                                     , self.cache)

    def search_in_cache(self, criteria):
        # return only one match of result_set in cache
        # example of match
        # {
        #  'address': (ip, port),
        #  'result_set': result_set,
        #  'servent_id': servent_id,
        # }
        for cache in self.cache:
            for result in cache['result_set']:
                if criteria == result['file_name']:
                    self.log("%s File is found in Cache.",
                            self.reactor.address)
                    return cache
        return False

    def search(self, criteria):
        # overwrite the default search from servent
        for fileinfo in self.files:
            if criteria == fileinfo.file_name:
                return fileinfo
        return False
