import uuid
from struct import unpack, pack, calcsize
from messagebody import GnutellaBodyId, PingBody, PongBody, PushBody, QueryBody, QueryHitBody

class Message:
    # count in byte
    MAXIMUM_SUM_TTL_HOPS = 7
    
    def __init__(self, message_id = None, ttl = 7):
        if message_id:
            self.message_id = message_id
        else:
            # automatically generate one
            self.message_id = uuid.uuid4().bytes
        self.ttl = ttl
        self.hops = 0
        self.body = None
        self.payload_length = None
        self.payload_descriptor = None
        self.fmt = '!16sBBBI'
        self.HEADER_LENGTH = calcsize(self.fmt)
            
    def decrease_ttl(self, value=1):
        self.ttl = self.ttl - value
        self.hops = self.hops + value
    
    def serialize(self):
        assert self.body != None
        assert self.payload_descriptor != None
        payload = self.body.serialize()
        self.payload_length = len(payload)
        header = pack(self.fmt, self.message_id, self.payload_descriptor, self.ttl, self.hops, self.payload_length)        
        return header + payload
    
    def deserialize(self, raw_data):
        if len(raw_data) < self.HEADER_LENGTH:
            return None
        self.message_id, self.payload_descriptor, self.ttl, self.hops, self.payload_length = unpack(self.fmt, raw_data[:self.HEADER_LENGTH])
        # Check for error heuristically in connection stream
        if not (self.payload_descriptor == GnutellaBodyId.PING or 
                self.payload_descriptor == GnutellaBodyId.PONG or 
                self.payload_descriptor == GnutellaBodyId.PUSH or 
                self.payload_descriptor == GnutellaBodyId.QUERY or 
                self.payload_descriptor == GnutellaBodyId.QUERYHIT):
            raise ValueError
        if self.hops + self.ttl > self.MAXIMUM_SUM_TTL_HOPS:
            raise ValueError
        # shorten the raw_data to body
        raw_data = raw_data[self.HEADER_LENGTH:]
        # if check raw_data has enough data for payload
        if len(raw_data) < self.payload_length:
            return None
        # deserialize the body
        if self.payload_descriptor == GnutellaBodyId.PING:
            self.body = PingBody(self)
        elif self.payload_descriptor == GnutellaBodyId.PONG:
            self.body = PongBody(self)
        elif self.payload_descriptor == GnutellaBodyId.PUSH:
            self.body = PushBody(self)
        elif self.payload_descriptor == GnutellaBodyId.QUERY:
            self.body = QueryBody(self)
        elif self.payload_descriptor == GnutellaBodyId.QUERYHIT:
            self.body = QueryHitBody(self)
        else:
            raise ValueError('message type is not one of PING, PONG, QUERY, QUERYHIT, PUSH')
        # final check if deserialize correctly with payload_length given in the header
        if self.body.deserialize(raw_data[:self.payload_length]) == None:
            raise ValueError("body should be able to deserialize")
        return self.payload_length + self.HEADER_LENGTH
    
    def __repr__(self):        
        return "<Message: %s %s %s %s>" % (self.message_id.encode('hex_codec'), GnutellaBodyId.get_str_id(self.payload_descriptor), self.ttl, self.hops)
        
def create_message(message_type, message_id = None, ttl = 7, **kwargs):
    message = Message(message_id, ttl)
    if message_type == GnutellaBodyId.PING:
        PingBody(message)
    elif message_type == GnutellaBodyId.PONG:
        PongBody(message, kwargs['ip'], kwargs['port'], kwargs['num_of_files'], kwargs['num_of_kb'])
    elif message_type == GnutellaBodyId.PUSH:
        PushBody(message, kwargs['servent_id'], kwargs['ip'], kwargs['port'], kwargs['file_index'])
    elif message_type == GnutellaBodyId.QUERY:
        QueryBody(message, kwargs['min_speed'], kwargs['search_criteria'])
    elif message_type == GnutellaBodyId.QUERYHIT:
        QueryHitBody(message, 
                     kwargs['num_of_hits'], 
                     kwargs['ip'], 
                     kwargs['port'], 
                     kwargs['speed'], 
                     kwargs['result_set'], 
                     kwargs['servent_id'])
    else:
        raise ValueError('message type is not one of PING, PONG, QUERY, QUERYHIT, PUSH')    
    return message

