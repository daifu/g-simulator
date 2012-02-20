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

    def check_file(self, file_id):
        """
        check if the servent have the file with id = file_id
        """
    
    # TODO
    # set and get methods for: hostName/ip, portNum, nums_files_share and array_of_file_share 
    # 1 more get and set method for something called Reactor (socketPool)
    # as Howard want

    def create_message(self, peer_id, messageID, message):
        """ 
        creating a message, not sure if the input argument is enough 
        """
        # TODO
        if messageID == GnutellaBodyId.PIND:
            body = PingBody(message)
        elif messageID == GnutellaBodyId.POND:
            body = PongBody(message)
        elif messageID == GnutellaBodyId.QUERY:
            body = QueryBody(message)
        elif messageID == GnutellaBodyId.QUERYHIT:
            body = QueryHitBody(message)
        elif messageID == GnutellaBodyId.PUSH:
            body = PushBody(message)
        else:
            return
        
        self.message = Message()
        self.message.setBody(body)
        self.reactor.send(peer_id, message)
        
    def on_connect(self, peerID):
        """ TODO (my part)"""
        """ what to do when a servent connect to a network """

    def on_receive(self, peerID, message):
        """ TODO (my part) """
        """ servent behavior when receiving a message """

    def on_disconnect(self, peerID):
        """ TODO (my part) """
        """ servent behavior when leaving the network """

    def on_error(self, peerID):
        """ TODO (my part) """
        """ servent behavior when timeout and/or pause message """

