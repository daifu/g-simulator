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
        self.logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        self.message = message
        self.message.body = self
        return

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
        self.message.payload_descriptor = GnutellaBodyId.PING
        return

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
        self.message.payload_descriptor =  GnutellaBodyId.PONG
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

    def serialize(self):
        assert self.ip != None
        assert self.port != None
        assert self.num_of_files != None
        assert self.num_of_kb != None     
        body = pack('!H', self.port) + pack('<L', self.ip) + pack('!II', self.num_of_files, self.num_of_kb)
        return body

    def deserialize(self, raw_data):        
        if not len(raw_data) == self.__length:
            return None
        self.port = unpack('!H', raw_data[:2])[0]
        self.ip = unpack('<L', raw_data[2:6])[0]        
        self.num_of_files, self.num_of_kb = unpack('!II', raw_data[6:14])
        return self.__length

class PushBody(IMessageBody):
    """
    Push body include Servent Identifier, File Index, IP Address, Port
    """
    def __init__(self, message, servent_id = None, ip = None, port = None, file_index = None):
        IMessageBody.__init__(self, message)
        self.message.payload_descriptor = GnutellaBodyId.PUSH
        self.servent_id = servent_id
        self.ip = ip
        self.port = port
        self.file_index = file_index
        self.fmt = "!16sILH"
        return

    def serialize(self):
        assert self.servent_id != None
        assert self.file_index != None
        assert self.ip != None
        assert self.port != None
        body = pack(self.fmt, self.servent_id, self.file_index, self.ip, self.port)
        return body

    def deserialize(self, raw_data):
        size = calcsize(self.fmt)
        if not len(raw_data) == size:
            return None        
        self.servent_id, self.file_index, self.ip, self.port = unpack(self.fmt, raw_data[:size])
        return size


class QueryBody(IMessageBody):
    """
    Query body includes minimum speed, search criteria
    """
    def __init__(self, message, min_speed = None, search_criteria = None):
        IMessageBody.__init__(self, message)
        self.message.payload_descriptor = GnutellaBodyId.QUERY
        self.min_speed = min_speed
        self.search_criteria = search_criteria
        # The parameter could set to None, because it meants to deseralize a raw_data packet
        self.fmt = ""
        return

    def serialize(self):
        assert self.min_speed != None
        assert self.search_criteria != None
        self.fmt = "!B%ss" % (len(self.search_criteria) + 1)        
        body = pack(self.fmt, self.min_speed, self.search_criteria)
        return body

    def deserialize(self, raw_data):
        if len(raw_data) > 1 and raw_data[1:].count('\x00') > 0:
            self.min_speed = unpack('!B', raw_data[0])[0]
            raw_data = raw_data[1:]            
            self.search_criteria = raw_data[:raw_data.index('\x00')]
            return 2+len(self.search_criteria)
        else:
            return None        

class QueryHitBody(IMessageBody):
    """
    Query hit body includes number of hits, port, ip address, speed, result
    set, servent identifier.
    
    Result set include file index, file size, and file name
    """
    def __init__(self, message, num_of_hits = None, ip = None, port = None, speed = None, result_set = None, servent_id = None):
        IMessageBody.__init__(self, message)
        self.message.payload_descriptor = GnutellaBodyId.QUERYHIT
        self.ip = ip
        self.port = port
        self.speed = speed
        self.result_set = result_set
        self.servent_id = servent_id
        self.num_of_hits = num_of_hits
        return

    def serialize(self):
        assert self.num_of_hits != None
        assert self.ip != None
        assert self.port != None
        assert self.speed != None
        assert self.result_set != None
        assert self.servent_id != None
        body = pack("!BHLI", self.num_of_hits, self.port, self.ip, self.speed)
        for result in self.result_set:
            fmt = "!iI%ss" % (len(result['file_name'])+2)                        
            body += pack(fmt, result['file_index'], result['file_size'], result['file_name'])
        return body + self.servent_id

    def deserialize(self, raw_data):
        # total_size maintain number of bytes used up in deserialize
        total_size = 0
        fmt = "!BHLI"
        size = calcsize(fmt)
        if len(raw_data) > size:
            self.num_of_hits, self.port, self.ip, self.speed = unpack(fmt, raw_data[:size])
            self.result_set = []
            raw_data = raw_data[size:]
            total_size += size
            fmt = "!iI"
            size = calcsize(fmt)
            for _ in range(0, self.num_of_hits):
                if len(raw_data) < size:
                    return None
                file_index, file_size = unpack(fmt, raw_data[:size])
                raw_data = raw_data[size:]
                total_size += size
                if raw_data.count('\x00\x00') == 0:
                    return None
                file_name = raw_data[:raw_data.index('\x00\x00')]
                raw_data = raw_data[len(file_name)+2:]
                total_size += len(file_name)+2
                self.result_set.append({'file_index': file_index, 'file_size': file_size, 'file_name': file_name})
            if len(raw_data) < 16:
                return None
            self.servent_id = raw_data[:16]
            return total_size + 16                   
        else:
            return None