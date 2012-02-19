import logging

class IMessageBody:
    """
    This is the interface for all message body in Gnutella network
    """
    def __init__(self, message):
        self.message = message
        self.logger = logging.getLogger(__name__)
    
    def serialize(self):
        """
        return a byte array representation of body to send over network socket
        """
        pass
    
    def deserialize(self, raw_data):
        """
        throw exception in deserialize
        """
        pass
    
class PingBody(IMessageBody):
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class PongBody(IMessageBody):
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class PushBody(IMessageBody):
    def __init__(self, message):
        IMessageBody.__init__(self, message)
    
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class QueryBody(IMessageBody):
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass
    
class QueryHitBody(IMessageBody):
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        
    def serialize(self):
        # TODO: implement this method
        pass
    
    def deserialize(self, raw_data):
        # TODO: implement this method
        pass