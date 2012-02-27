import logging
from struct import pack, unpack, calcsize

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
    def __init__(self, message, ip = None, port = None, num_of_files = None, num_of_kb = None):
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

    def deserialize(self, raw_data):        
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
    def __init__(self, message, servant_id = None, ip = None, port = None, file_index = None):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.PUSH)
        self.servant_id = servant_id
        self.ip = ip
        self.port = port
        self.file_index = file_index
        self.fmt = "!16sIIH"
        return

    def get_length(self):
        return calcsize(self.fmt)

    def serialize(self):
        body = pack(self.fmt, self.servant_id, self.file_index, self.ip, self.port)
        return body

    def deserialize(self, raw_data):
        if not len(raw_data) == self.length():
            return None        
        self.servant_id, self.file_index, self.ip, self.port = unpack(self.fmt, raw_data)
        return self.get_length()


class QueryBody(IMessageBody):
    """
    Query body includes minimum speed, search criteria
    """
    def __init__(self, message, min_speed = None, search_criteria = None):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(GnutellaBodyId.QUERY)
        self.min_speed = min_speed
        self.search_criteria = search_criteria
        # The parameter could set to None, because it meants to deseralize a raw_data packet
        self.fmt = ""
        return

    def get_length(self):
        self.fmt = "!B%ss" % (len(self.search_criteria) + 1)
        return calcsize(self.fmt)

    def serialize(self):
        self.fmt = "!B%ss" % (len(self.search_criteria) + 1)        
        body = pack(self.fmt, self.min_speed, self.search_criteria)
        return body

    def deserialize(self, raw_data):
        if len(raw_data) > 1 and raw_data[1:].count('\0') > 0:
            self.min_speed = unpack('!B', raw_data[0])
            raw_data = raw_data[1:]            
            self.search_criteria = self.raw_data[:raw_data.index('\0')]
            return 2+len(self.search_criteria)
        else:
            return None        

class QueryHitBody(IMessageBody):
    """
    Query hit body includes number of hits, port, ip address, speed, result
    set, servent identifier.
    result set include file index, file size, and file name
    """

    def __init__(self, message, num_of_hits = None, ip = None, port = None, speed = None, result_set = None, servent_id = None):
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

    def deserialize(self, raw_data):
        """
        Return a tuple of (ip, port, speed, servent_id, 
                           file_index, file_size, file_name
                           ...repeat result_set...)
        """
        if raw_data is "":
            raw_data = self.body
        return unpack(self.fmt, raw_data)
