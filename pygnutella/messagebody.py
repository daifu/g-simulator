import logging

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
    parameter for message is '' or empty string
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(0x00)
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
    Example for message dictionary:
    message = {
            'port': 3000,
            'ip_address': '192.168.1.1',
            'number_of_file_shared': 1,
            'number_of_kb_shared': 30
        }
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(0x01)
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
    Example for message dictionary:
    message = {
            'servent_identifier': 'binarystring' # 16 byte string uniquely
            identifying the servent on the network who is being requested to
            push the file with index File_Index.
            'file_index': 'index string' # The index uniquely identifying the
            file to be pushed from the target servent.
            'ip_address': '192.168.1.2' # the ip of host should be pushed
            'port': '3000' # the port of host should be pushed
        }
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(0x40)
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
    Example of message dictionary:
    message = {
            'minimum_speed': '100' # the unit is kB/sec of servents should be
            respond to this message.
            'search_criteria': 'something string.\n' # \n is the terminator of
            the string and the max length of the this string is bounced by
            payload_length.
        }
    """
    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(0x80)
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
    Example of message dictionary:
    message = {
            'number_of_hits': 2, # the number of query hits in the result set.
            'port': 3000, # the port number on which the responding host can
            accept incoming connections.
            'ip_address': '192.168.1.3', # the ip address of the responding
            host.
            'speed': '100', # the unit is in kB/sec of the responding host.
            'result_set': [
                {
                    'file_index': 2,
                    'file_size': 100,
                    'file_name': 'the dark night'
                },
                {
                    'file_index': 3,
                    'file_size': 200,
                    'file_name': 'dark night, King'
                }
            ], # need to add a terminator for the filename, such as \n.
            'servent_id': 'unique string' # 16 byte sting uniquely identify the
            responding servent on the network.
        }
    """

    def __init__(self, message):
        IMessageBody.__init__(self, message)
        self.message.set_payload_descriptor(0x81)
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
