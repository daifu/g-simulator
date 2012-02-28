import logging
import uuid
from reactor import Reactor
from messagebody import GnutellaBodyId, PingBody, PongBody, PushBody, QueryBody, QueryHitBody
from message import Message

# struct of file, each servent have an array/list of these files
class FileInfo:
    file_id = 0
    file_name =  ""
    file_size = 0

# a node is another servent, each servent have an array/list of other servents
# in the network, up to 7 hops from it
class ServentInfo:
    peer_id = 0
    hop_num = 0
    
class ServentList:
    node = [] # node is another servent, refer to ServentInfo above
    message_id = 0
    
class Servent:
    def __init__(self, port, files = []):
        self.logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))
        self.files = files
        # push_list: message_id of ping message -> connection_handlers
        self.ping_list = {}
        # push_list: message_id of query message -> connection_handlers
        self.query_list = {}
        # push_list: message_id of push message -> connection_handlers  
        self.push_list = {}
        # create Reactor class for socket management
        self.reactor = Reactor(port)
        self.reactor.install_handlers(self.on_accept, self.on_connect, self.on_receive, self.on_disconnect)
        # create servent id
        self.id = uuid.uuid1().bytes
        return
    
    def on_accept(self):
        """
        on event of gnutella connection, accept or refuse depends on
        resource management
        """
        # Always accept new connection
        return True
    
    def on_connect(self, connection_handler):
        """ 
        on event of a servent connects to 
        """
        # Create and send a ping message
        self.create_message(connection_handler, GnutellaBodyId.PING)
        return

    def on_receive(self, connection_handler, message):
        """ 
        on event of receiving a message from an existing connection 
        """
        self.logger.debug('Receive message from %s', connection_handler.socket.getsockname())
        # decrease ttl and increase hop
        ttl = message.get_ttl()
        hops = message.get_hops()
        message_id = message.get_message_id()        
        # Routing only if time to live > 1
        if ttl > 1:                
            if message.get_payload_descriptor() == GnutellaBodyId.PING:                     
                # send Ping to any neighbor that not the one servent recceived the Ping from
                self.forward_ping(connection_handler, message_id, ttl-1, hops+1)
                # add ping message_id to seem list to forward pong later
                self.ping_list[message_id] = connection_handler
                # reply with Pong (the return trip's ttl should be equals to hops)
                pong_message = Message(message_id, hops, 0)
                # TODO: fixed number of files share and number of kilobyte shared              
                PongBody(pong_message, self.reactor.ip, self.reactor.port, 2, 2)
                connection_handler.send_message(pong_message)
            elif message.get_payload_descriptor() == GnutellaBodyId.PONG:
                # Forward pong back on the same path                
                try:
                    message.decrease_ttl()
                    message.increase_hop()
                    self.ping_list[message_id].send_message()
                except KeyError:
                    pass
            elif message.get_payload_descriptor() == GnutellaBodyId.QUERY:
                # TODo
                # servent behavior when receiving QUERY message
                pass
            elif message.get_payload_descriptor() == GnutellaBodyId.QUERYHIT:
                # TODO
                # servent behavior when receiving QUERYHIT message
                pass
            elif message.get_payload_descriptor() == GnutellaBodyId.PUSH:
                # TODO
                # servent behavior when receiving PUSH message
                pass
            else:
                raise ValueError
            
    def on_disconnect(self, connection_handler):
        """ 
        servent behavior when leaving the network 
        """
        self.logger.debug('disconnect from the network %s', connection_handler.socket.getsockname())
        # TODO: resource clean up i.e. ping_list, etc...
        return
    
    def forward_ping(self, connection_handler, message_id, ttl, hops):
        """
        Forward Ping packet to every directly connected servent
        """
        message = Message(message_id, ttl, hops)
        PingBody(message)
        self.reactor.broadcast_except_for(connection_handler, message)
        return
    
    # each member of files is a FileInfo    
    def set_files(self, files):
        self.files = files
        return

    def get_files(self, files):
        return files

    def check_file(self, file_id):
        """
        check if the servent have the file with id = file_id
        """
        # iterate through the file list fo find the file
        # files is array/dict, w/e of file_id
        for item in self.files:
            if item == file_id:
                return True
        return False

    def search(self, criteria):
        # search the files with criteria
        # TODO: right now, return empty list                
        return []    