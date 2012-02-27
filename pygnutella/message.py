import logging
import hashlib
import struct

class Message:
    def __init__(self, message_id, ttl = 7, hops = 0):
        self.logger = logging.getLogger(__name__)
        self.message_id = message_id
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
        m = hashlib.md5()
        # TODO: generate message id
        m.update("This need to be change")
        message_id = m.digest()        
        payload = self.body.serialize()
        self.payload_length = len(payload)
        header = struct.pack('!bbbi', self.payload_descriptor, self.ttl, self.hops, self.payload_length)        
        return message_id + header + payload
    
    def deserialize(self, raw_data):
        # TODO: implement this function
        pass
        
        
    
