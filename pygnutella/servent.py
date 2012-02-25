# -*- coding: cp1252 -*-
import logging
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
    def __init__(self, ip, port, files = []):
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.files = files

        self.peer_id_set = [] # array of servent info
        self.ping_list = {} # a dict that map message_id to a servent
        self.query_list = {} # a dict that map message_id to a servent 
        self.push_list = {} # a dict that map message_id to a servent
        
        self.reactor = Reactor((ip, port))
        # TODO: fix this
        self.reactor.install_handlers(None, None, None, None)
        # TODO: create servent id
        self.id = ''

    # each member of files is a FileInfo    
    def set_files(self, files):
        self.files = files

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

    def get_result_set(self, criteria):
        """
        search the file array to file the file with the criteria and put it
        into result set
        """
        # TODO
        return self.result_set

    def search_criteria(self, criteria):
        # TODO
        # search the files with criteria
        return False
    
    def get_peer_id_set(self):
        """
        get a set of peer_id that the servent currently connect to
        """
        # TODO
        return self.peer_id_set

    def add_to_ping_list(self, new_servent, message_id):
        """
        add a peer's id that send a ping message to ping_list
        """
        # just gieve it a try, should test it somehow
        self.ping_list[message_id] = new_servent
        
    def get_ping_list(self):
        """
        a list/array of serventand message_id that the servent receive the ping from
        """
        # TODO
        # right now just need a method to make it work
        return self.ping_list

    def add_to_query_list(self, new_servent, message_id):
        """
        add a peer's id that send a query message to query_list
        """
        self.query_list[message_id] = new_servent

    def get_query_list(self):
        """
        a list/array of serventand message_id that the servent receive the ping from
        """
        return self.query_list
    
    # TODO
    # set and get methods for: hostName/ip, portNum, nums_files_share and array_of_file_share 
    # 1 more get and set method for something called Reactor (socketPool)
    # as Howard want

    def create_message(self, peer_id, body_id, message_id, ttl = 7, hops = 0):
        """ 
        creating a message, not sure if the input argument is enough
        this also send the message after creating it
        """
        # Create message
        message = Message(ttl, hops, message_id)
        # Create message body
        if body_id == GnutellaBodyId.PING:
            body = PingBody(message)
        elif body_id == GnutellaBodyId.PONG:
            # create pong body data
            ip = self.ip
            port = self.port
            num_of_files = self.get_files 
            num_of_kb = 0 #  TODO: get the real number
            body = PongBody(message, ip, port, num_of_files, num_of_kb)
        elif body_id == GnutellaBodyId.QUERY:
            # create query body data
            min_speed = 100 # default is 100 kB/sec
            search_criteria = '' # TODO: get the real string
            body = QueryBody(message, min_speed, search_criteria)
        elif body_id == GnutellaBodyId.QUERYHIT:
            # create queryhit body data
            ip = self.ip
            port = self.port
            speed = 100 # default is 100 kB/sec
            result_set = [] # TODO: create real resut set
            servent_id = self.id
            num_of_hits = 0 # TODO: create number of hits
            body = QueryHitBody(message, ip, port, speed, 
                                result_set, servent_id, num_of_hits)
        elif body_id == GnutellaBodyId.PUSH:
            # create push body data
            ip = self.ip
            port = self.port
            file_index = '' # TODO: a index that find the file from the servent
            body = PushBody(message, ip, port, file_index)
        else:
            return
        # Put body into the message        
        message.set_body(body)
        message.set_payload_length(body.get_length()) # get body length
        # Send message to peer with peer_id
        self.reactor.send(peer_id, message)
        
    def on_connect(self, peer_id):
        """ what to do when a servent connect to a network """
        # Servent create and send a ping message
        self.create_message(peer_id, GnutellaBodyId.PING)

    def on_receive(self, peer_id, message):
        """ servent behavior when receiving a message """
        logging.debug('Receive message from ' + peer_id + '\n')

        """ decrease ttl and increase hop """
        ttl = message.get_ttl()
        hops = message.get_hops()
        message_id = message.get_message_id()

        """ if ttl = 0, the message is "dead", do not need to forward it """
        if message.get_payload_descriptor() == GnutellaBodyId.PING:
            # TODO
            """
            Implementation: - search through the servent's neighbor peer_id
            list and send ping message to any peer not the one who the servent
            get the PING from and 1 hop from the servent
                            - respond peer_id with PONG
                            - add the servent that send the PING to this servent's
                              ping-list
            """
            self.create_message(peer_id, GnutellaBodyId.PONG, 7, 0, message_id)
            new_servent.peer_id = peer_id;
            new_servent.hop = 1;
            self.add_to_ping_list(new_servent, message_id)

            # send PING to any neighbor that not the one servent recceived the PING from
            if ttl > 1:
                for item in self.get_peer_id_set:
                    if item.peer_id != peer_id and item.hop_num == 1:
                        self.create_meassage(item.peer_id, GnutellaBodyId.PING, ttl-1, hops+1, message_id)
                
        if message.get_payload_descriptor() == GnutellaBodyId.PONG:
            # TODO
            """
            Implementation: - search the ping_list and forward the PONG message
            if ttl > 0
            """
            if ttl > 1:
                return_peer_id = self.ping_list[message_id].peer_id
                self.create_message(return_peer_id, GnutellaBodyId.PONG, ttl-1, hop+1, message_id)

        if message.get_payload_descriptor() == GnutellaBodyId.QUERY:
            # servent behavior when receiving QUERY message
            """
            Implementation: - add the servent to query_list
                            - search the file list for the criteria, if it hit,
            return with query hit
                            - send query to neighbor servent
            """
            new_servent.peer_id = peer_id;
            new_servent.hop = 1;
            self.add_to_query_list(new_servent, message_id)

            if search_criteria(criteria) == True:
                self.create_message(peer_id, GnutellaBodyId.QUERY, ttl-1, hop+1, message_id)

            # send PING to any neighbor that not the one servent recceived the QUERY from
            if ttl > 1:
                for item in self.get_peer_id_set:
                    if item.peer_id != peer_id and item.hop_num == 1:
                        self.create_meassage(item.peer_id, GnutellaBodyId.QUERY, ttl-1, hops+1, message_id)
            
        if message.get_payload_descriptor() == GnutellaBodyId.QUERYHIT:
            # TODO
            # servent behavior when receiving QUERYHIT message
            pass
        if message.get_payload_descriptor() == GnutellaBodyId.PUSH:
            # TODO
            # servent behavior when receiving PUSH message
            pass
            
    def on_disconnect(self, peer_id):
        """ servent behavior when leaving the network """
        # TODO
        logging.debug(peer_id + ': disconneting from the network\n')
    
    def on_error(self, peer_id):
        """ servent behavior when timeout and/or pause message """
        # TODO
        logging.debug(peer_id + ': error occur\n')
