from ..servent import BasicServent
from ..messagebody import GnutellaBodyId
from ..message import create_message
import time

class QueryServent(BasicServent):
    """
    BasicServent does not reply to query message.
    But this servent does.
    """
    
    def on_receive(self, connection_handler, message):        
        if message.payload_descriptor == GnutellaBodyId.QUERY:
            forward_key = (message.message_id, GnutellaBodyId.QUERYHIT)
            now = time.time()
            # check if I already replied to this query            
            not_seen_or_expire = forward_key not in self.forwarding_table or (self.forwarding_table[forward_key][1] < now)
            # check if this is my query
            not_ignore_or_expire = message.message_id not in self.ignore or (self.ignore[message.message_id] < now)
            if not_seen_or_expire and not_ignore_or_expire:
                results = self.search(message.body.search_criteria)
                result_set = [result.get_result_set() for result in results]
                queryhit_message = create_message(GnutellaBodyId.QUERYHIT,
                                                  ip = self.reactor.ip,
                                                  port = self.reactor.port,
                                                  speed = 10, # TODO: how do you know what speed?
                                                  result_set = result_set)
                # send back the result
                self.send_message(queryhit_message, connection_handler)
            

