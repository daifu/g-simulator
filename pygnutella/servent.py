# -*- coding: cp1252 -*-
import logging
from reactor import Reactor
from messagebody import GnutellaBodyId, PingBody, PongBody, PushBody, QueryBody, QueryHitBody
from message import Message

class PingList:
    peer_id = 0
    message_id = 0
    
class Servent:
    def __init__(self, ip, port, files = []):
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.files = files
        self.reactor = Reactor((ip, port))
        # TODO: fix this
        self.reactor.install_handlers(None, None, None, None)
        # TODO: create servent id
        self.id = ''
        
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

    def get_peer_id_set(self):
        """
        get a set of peer_id that the servent currently connect to
        """
        # TODO
        return self.peer_id_set

    def add_to_ping_list(peer_id, message_id):
        """
        add a peer's id that send a ping message to ping_list
        """
        # TODO
        # don't know how array/vector/..w/e in python work
        # someone should do it
        
    def get_ping_list(self):
        """
        a list/array of IP and message_id that the servent receive the ping from
        """
        # TODO
        # right now just need a method to make it work
        return self.ping_list
    
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
            get the PING from
                            - respond peer_id with PONG
            """
            self.create_message(peer_id, GnutellaBodyId.PONG, 7, 0, message_id)

            if ttl > 1:
                for item in self.get_peer_id_set:
                    if item != peer_id:
                        self.create_meassage(item, GnutellaBodyId.PING, ttl-1, hops+1, message_id)
                
        if message.get_payload_descriptor() == GnutellaBodyId.PONG:
            # TODO
            """
            Implementation: - search the ping_list and forward the PONG message
            if ttl > 0
            """
            if ttl > 1:
                for item in self.get_ping_list():
                    if item.message_id == message.get_message_id():
                        self.create_message(item.peer_id, GnutellaBodyId.PONG, ttl-1, hop+1, message_id)

        if message.get_payload_descriptor() == GnutellaBodyId.QUERY:
            # TODO
            # servent behavior when receiving QUERY message
            pass
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
