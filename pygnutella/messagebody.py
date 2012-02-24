import logging
import struct

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
    def __init__(self, message, ip, port, num_of_files = 0, num_of_kb = 0):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.PONG)
        self.ip = ip
        self.port = port
        self.num_of_files = num_of_files
        self.num_of_kb = num_of_kb

        self.fmt = ""
        self.body = ""
        return

    def get_length(self):
        return struct.calcsize(self.fmt)

    def serialize(self):
        self.fmt = "!%ssiii" % len(self.ip)
        self.body = struct.pack(self.fmt, 
                                self.ip, 
                                self.port, 
                                self.num_of_files, 
                                self.num_of_kb)
        return self.body

    def deserialize(self, raw_data = ""):
        if raw_data is "":
            raw_data = self.body
        return struct.unpack(self.fmt, raw_data)

class PushBody(IMessageBody):
    """
    Push body include Servent Identifier, File Index, IP Address, Port
    """
    def __init__(self, message, ip, port, file_index):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.PUSH)
        self.ip = ip
        self.port = port
        self.file_index = file_index
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
    def __init__(self, message, min_speed, search_criteria):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.QUERY)
        self.min_speed = min_speed
        self.search_criteria = search_criteria
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

    def __init__(self, message, ip, port, speed, result_set, servent_id, num_of_hits):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.QUERYHIT)
        self.ip = ip
        self.port = port
        self.speed = speed
        self.result_set = result_set
        self.servent_id = servent_id
        self.num_of_hits = num_of_hits
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
