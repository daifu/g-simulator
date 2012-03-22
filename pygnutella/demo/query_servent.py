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
            not_seen_or_expired = forward_key not in self.forwarding_table or (self.forwarding_table[forward_key][1] < now)
            # check if this is my query
            not_ignore_or_expired = message.message_id not in self.ignore or (self.ignore[message.message_id] < now)
            if not_seen_or_expired and not_ignore_or_expired:
                results = self.search(message.body.search_criteria)
                # if there is a match
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
        # use default behavior
        BasicServent.on_receive(self, connection_handler, message)
            

