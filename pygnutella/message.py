import logging
import hashlib
import struct

class Message:
    def __init__(self, ttl = 7, hops = 0):
        self.logger = logging.getLogger(__name__)
        self.ttl = ttl
        self.hops = hops
        self.body = None
        self.payload_length = None
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
        self.set_payload_length(self.body.get_length())
        # TODO: generate message id
        m = hashlib.md5()
        m.update("This need to be change")
        message_id = m.digest()        
        header = struct.pack('!bbbi', self.payload_descriptor, self.ttl, self.hops, self.payload_length)
        payload = self.body.serialize()
        return message_id + header + payload
    
    def deserialize(self, raw_data):
        # TODO: implement this function
        pass
        
        
    
