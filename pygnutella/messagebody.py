import logging

class GnutellaBodyId:
    PING = 0x00
    PONG = 0x01
    QUERY = 0x80
    QUERYHIT = 0x81
    PUSH = 0x40

class IMessageBody:
    """
    This is the interface for all message body in Gnutella network
    """
    def __init__(self, message):
        self.logger = logging.getLogger(__name__)
        self.message = message
        self.message.set_body(self)
        return
    
    def get_length(self):
        """
        Return length in byte of representation of the body
        """
        raise NotImplementedError
    
    def serialize(self):
        """
        Return a byte array representation of body to send over network socket
        """
        raise NotImplementedError
    
    def deserialize(self, raw_data):
        """
        Return either None or NextMessageIndex
        """
        raise NotImplementedError
    
class PingBody(IMessageBody):
    """
    Ping body have no associated payload and are of zero length
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.PING)
        return
    
    def get_length(self):
        return 0
    
    def serialize(self):
        return b''
            
    def deserialize(self, raw_data):
        return 0
        
    
class PongBody(IMessageBody):
    """
    Pong body include Port, IP Address, Number of Files Shared, Number of Kilobytes Shared.
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.PONG)
        return
    
    def get_length(self):
        # TODO: implement this method
        pass
        
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class PushBody(IMessageBody):
    """
    Push body include Servent Identifier, File Index, IP Address, Port
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.PUSH)
        return

    def get_length(self):
        # TODO: implement this method
        pass
        
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class QueryBody(IMessageBody):
    """
    Query body includes minimum speed, search criteria
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.QUERY)
        return

    def get_length(self):
        # TODO: implement this method
        pass
            
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class QueryHitBody(IMessageBody):
    """
    Query hit body includes number of hits, port, ip address, speed, result
    set, servent identifier.
    """

    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.QUERYHIT)
        return

    def get_length(self):
        # TODO: implement this method
        pass
                    
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
