import logging

class Message:
    def __init__(self, ttl = 7, hops = 0):
        self.logger = logging.getLogger(__name__)
        self.tll = ttl
        self.hops = hops
        self.body = None
        self.payload_length = 0
        self.payload_descriptor = None
        
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
    
    def serialize(self):
        # TODO: implement this function
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this function
        pass
        
        
    