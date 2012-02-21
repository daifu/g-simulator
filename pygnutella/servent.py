import logging
from reactor import Reactor
from messagebody import GnutellaBodyId, PingBody, PongBody, PushBody, QueryBody, QueryHitBody
from message import Message

class Servent:
    def __init__(self, ip, port, files = []):
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.files = files
        self.reactor = Reactor((ip, port))
        # TODO: fix this
        self.reactor.install_handlers(None, None, None, None)
        
    def set_files(self, files):
        self.files = files

    def get_files(self, files):
        return files

    def check_file(self, file_id):
        """
        check if the servent have the file with id = file_id
        """
        # iterate through the file list fo find the file
        for item in self.files:
            if item == file_id:
                return True
        return False
    
    # TODO
    # set and get methods for: hostName/ip, portNum, nums_files_share and array_of_file_share 
    # 1 more get and set method for something called Reactor (socketPool)
    # as Howard want

    def create_message(self, peer_id, body_id):
        """ 
        creating a message, not sure if the input argument is enough
        this also send the message after creating it
        """
        # Create message
        message = Message()
        # Create message body
        if body_id == GnutellaBodyId.PING:
            body = PingBody(message)
        elif body_id == GnutellaBodyId.PONG:
            body = PongBody(message)
        elif body_id == GnutellaBodyId.QUERY:
            body = QueryBody(message)
        elif body_id == GnutellaBodyId.QUERYHIT:
            body = QueryHitBody(message)
        elif body_id == GnutellaBodyId.PUSH:
            body = PushBody(message)
        else:
            return
        # Put body into the message        
        message.setBody(body)
        # Send message to peer with peer_id
        self.reactor.send(peer_id, message)
        
    def on_connect(self, peer_id):
        """ what to do when a servent connect to a network """
        # Servent create and send a ping message
        self.create_message(peer_id, GnutellaBodyId.PING)

    def on_receive(self, peer_id, message):
        """ servent behavior when receiving a message """
        if message.get_payload_descriptor() == GnutellaBodyId.PING:
            # TODO
            # servent behavior when receiving PING message
            pass
        if message.get_payload_descriptor() == GnutellaBodyId.PONG:
            # TODO
            # servent behavior when receiving PONG message
            pass
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
