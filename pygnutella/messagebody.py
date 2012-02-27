import logging
from struct import *

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
        Return either None if incomplete or NextMessageIndex if complete buffered raw_data
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
        return ''

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
        # 2 bytes for port (NOTE: this is one byte extra from actual PONG)
        # 4 bytes for ip address
        # 4 bytes for number of files shared
        # 4 byte for number of kilobytes shared
        self.__length = 2+4+4+4
        return

    def get_length(self):
        return self.__length

    def serialize(self):        
        body = pack('!H', self.port) + pack('<I', self.ip) + pack('!II', self.num_of_files, self.num_of_kb)
        return body

    def deserialize(self, raw_data = ""):        
        if not len(raw_data) == self.length():
            return None
        self.port = unpack('!H', raw_data)
        self.ip = unpack('<I', raw_data[2:])
        self.num_of_files, self.num_of_kb = unpack('!II', raw_data[6:])
        return self.get_length()

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

        self.fmt = ""
        self.body = ""
        return

    def get_length(self):
        return calcsize(self.fmt)

    def serialize(self):
        self.fmt = "!%ssi%ss" % (len(self.ip),
                                 len(self.file_index))
        self.body = pack(self.fmt, 
                                self.ip, 
                                self.port, 
                                self.file_index)
        return self.body

    def deserialize(self, raw_data = ""):
        """
        Return a tuple of (ip, port, file_index)
        """
        if raw_data is "":
            raw_data = self.body
        return unpack(self.fmt, raw_data)


class QueryBody(IMessageBody):
    """
    Query body includes minimum speed, search criteria
    """
    def __init__(self, message, min_speed, search_criteria):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.QUERY)
        self.min_speed = min_speed
        self.search_criteria = search_criteria

        self.fmt = ""
        self.body = ""
        return

    def get_length(self):
        return calcsize(self.fmt)

    def serialize(self):
        self.fmt = "!i%ss" % len(self.search_criteria)
        self.body = pack(self.fmt,
                                self.min_speed,
                                self.search_criteria)
        return self.body

    def deserialize(self, raw_data = ""):
        """
        Return a tuple of (min_speed, search_criteria)
        """
        if raw_data is "":
            raw_data = self.body
        return unpack(self.fmt, raw_data)

class QueryHitBody(IMessageBody):
    """
    Query hit body includes number of hits, port, ip address, speed, result
    set, servent identifier.
    result set include file index, file size, and file name
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

        self.fmt = ""
        self.body = ""
        return

    def get_length(self):
        return calcsize(self.fmt)

    #No idea how to implement the result_set
    def serialize(self):
        self.fmt = "!%ssii%ss" % (len(self.ip),
                                  len(self.servent_id))
        self.body = pack(self.fmt, 
                                self.ip, 
                                self.port, 
                                self.speed, 
                                self.servent_id)

        #for the result_set, loop through it and append
        #it to fmt
        fmt = ""
        for result in self.result_set:
            fmt = "%ssi%ss" % (len(result['file_index']),
                                len(result['file_name']))
            self.fmt += fmt
            fmt = '!' + fmt
            self.body += pack(fmt, result['file_index'],
                                          result['file_size'],
                                          result['file_name'])
        return self.body

    def deserialize(self, raw_data = ""):
        """
        Return a tuple of (ip, port, speed, servent_id, 
                           file_index, file_size, file_name
                           ...repeat result_set...)
        """
        if raw_data is "":
            raw_data = self.body
        return unpack(self.fmt, raw_data)
