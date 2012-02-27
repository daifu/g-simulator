import logging
from struct import unpack, pack, calcsize
from messagebody import GnutellaBodyId, PingBody, PongBody, PushBody, QueryBody, QueryHitBody

class Message:
    # count in byte
    MAXIMUM_SUM_TTL_HOPS = 7
    
    def __init__(self, message_id = None, ttl = 7, hops = 0):
        self.logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        self.message_id = message_id
        self.ttl = ttl
        self.hops = hops
        self.body = None
        self.payload_length = None
        self.payload_descriptor = None
        self.fmt = '!16sbbbI'
        self.HEADER_LENGTH = calcsize(self.fmt)
        
    def set_body(self, body):
        self.body = body
        
    def get_body(self):
        return self.body
    
    def set_payload_length(self, payload_length):
        self.payload_length = payload_length
        
    def get_payload_length(self):
        return self.payload_length
    
    def set_payload_descriptor(self, payload_descriptor):
        self.payload_descriptor = payload_descriptor
        
    def get_payload_descriptor(self):
        return self.payload_descriptor

    def set_message_id(self, new_id):
        self.message_id = new_id

    def get_message_id(self):
        return self.message_id

    def get_ttl(self):
        return self.ttl
    
    def get_hops(self):
        return self.hops
    
    def decrease_ttl(self, value=1):
        self.ttl = self.ttl - value

    def increase_hop(self, value=1):
        self.hop = self.hop + value
    
    def serialize(self):             
        payload = self.body.serialize()
        self.payload_length = len(payload)
        header = pack(self.fmt, self.message_id, self.payload_descriptor, self.ttl, self.hops, self.payload_length)        
        return header + payload
    
    def deserialize(self, raw_data):
        if len(raw_data) < self.HEADER_LENGTH:
            return None
        self.message_id, self.payload_descriptor, self.ttl, self.hops, self.payload_length = unpack(self.fmt, raw_data[:self.HEADER_LENGTH])
        # Check for error heuristically in connection stream
        if not (self.payload_descriptor == GnutellaBodyId.PING or self.payload_descriptor == GnutellaBodyId.PONG or self.payload_descriptor == GnutellaBodyId.PUSH or self.payload_descriptor == GnutellaBodyId.QUERY or self.payload_descriptor == GnutellaBodyId.QUERYHIT):
            raise ValueError
        if self.hops + self.ttl > self.MAXIMUM_SUM_TTL_HOPS:
            raise ValueError
        # shorten the raw_data to body
        raw_data = raw_data[self.HEADER_LENGTH:]
        if len(raw_data) < self.payload_length:
            return None
        # deserialize the body
        if self.payload_descriptor == GnutellaBodyId.PING:
            self.body = PingBody()
        elif self.payload_descriptor == GnutellaBodyId.PONG:
            self.body = PongBody()
        elif self.payload_descriptor == GnutellaBodyId.PUSH:
            self.body = PushBody()
        elif self.payload_descriptor == GnutellaBodyId.QUERY:
            self.body = QueryBody()
        elif self.payload_descriptor == GnutellaBodyId.QUERYHIT:
            self.body = QueryHitBody()
        # final check if deserialize correctly with payload_length given in the header                              
        if self.body.deserialize(raw_data[:self.payload_length]):
            raise ValueError
        return self.payload_length + self.HEADER_LENGTH
        
        
    
