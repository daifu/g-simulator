from ..servent import BasicServent
from ..message import create_message
from ..messagebody import GnutellaBodyId
import time

class CacheServent(BasicServent):
    def __init__(self, bootstrap_address = None):
        # queryhit_cache is a list of tuple (servent_id, ip, port, files: list)
        self.queryhit_cache = []
        self.hits = 0
        self.misses = 0
        BasicServent.__init__(self, bootstrap_address=bootstrap_address)
        
    def on_receive(self, connection_handler, message):
        if message.payload_descriptor == GnutellaBodyId.QUERYHIT:
            self.save_queryhit(message)
        elif message.payload_descriptor == GnutellaBodyId.QUERY:
            forward_key = (message.message_id, GnutellaBodyId.QUERYHIT)
            now = time.time()
            # check if I already replied to this query
            not_seen_or_expired = forward_key not in self.forwarding_table or (self.forwarding_table[forward_key][1] < now)
            # check if this is my query
            not_ignore_or_expired = message.message_id not in self.ignore or (self.ignore[message.message_id] < now)
            if not_seen_or_expired and not_ignore_or_expired:
                # if there is a match
                results = self.search(message.body.search_criteria)
                if results:
                    result_set = [result.get_result_set() for result in results]
                    queryhit_message = create_message(GnutellaBodyId.QUERYHIT,
                                                      message_id = message.message_id,
                                                      ttl = message.hops+1,
                                                      ip = self.reactor.ip,
                                                      port = self.reactor.port,
                                                      speed = 1,
                                                      result_set = result_set,
                                                      servent_id = self.id)
                    # send back the result
                    self.send_message(queryhit_message, connection_handler)
                # now search the cache
                cache_results = self.search_queryhit(message.body.search_criteria)
                if cache_results:
                    for match in cache_results:
                        queryhit_message = create_message(GnutellaBodyId.QUERYHIT,
                                                          message_id = message.message_id,
                                                          ttl = message.hops+1,
                                                          ip = match[1],
                                                          port = match[2],
                                                          speed = 1,
                                                          result_set = match[3],
                                                          servent_id = match[0])
                        # send back the result
                        self.send_message(queryhit_message, connection_handler)
                    # if we found in cache, just don't use default behavior
                    return
        # use default behavior
        BasicServent.on_receive(self, connection_handler, message)
    
    def save_queryhit(self, message):
        match_servent = None
        # linear search through cache
        for cache_match in self.queryhit_cache:
            if cache_match[0] == message.body.servent_id and cache_match[1] == message.body.ip and cache_match[2] == message.body.port:
                match_servent = cache_match
                break
        if match_servent:
            # merge the result_set in message with current files_list we have on the servent
            files_list = match_servent[3]
            for queried_result in message.body.result_set:
                if queried_result not in files_list:
                    files_list.append(queried_result)
        else:
            # if we don't have, then insert new entry to cache
            entry = (message.body.servent_id, message.body.ip, message.body.port, message.body.result_set)
            self.queryhit_cache.append(entry)
            
   
    def search_queryhit(self, criteria):
        cache_result = []
        for cache_match in self.queryhit_cache:
            for result in cache_match[3]:
                # exact match
                if result['file_name'] == criteria:
                    entry = (cache_match[0], cache_match[1], cache_match[2], [result])
                    cache_result.append(entry)
                    # break to outer loop
                    break
        # keeping statistics
        if cache_result:
            self.hits += 1
        else:
            self.misses += 1
        return cache_result
