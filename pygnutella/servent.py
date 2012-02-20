# Servent class
# A node that connecet to other servent node through IP address and
# port number.
#

import logging;
import Reactor;

PIND_ID = 0x00
POND_ID = 0x01
QUERY_ID = 0x80
QUERYHIT_ID = 0x81
PUSH_ID = 0x40

class Servent:
    """
    Basic class for the servent
    """
    def __init__(self, ip, port, files = []):
        """
        docstring for __init__
        """
        self.ip = ip
        self.port = port
        self.files = files
        
    def setFiles(self, files):
        """
        docstring for setFiles
        """
        self.files = files

    """** TODO **"""
    """** set and get methods for: hostName/ip, portNum, nums_files_share **"""
    """** and array_of_file_share **"""
    """** 1 more get and set method for something called Reactor (socketPool) **"""
    """** as Howard want **"""

    def CreateMessage(self, peer_id, messageID, message):
        """ TODO (whoever do it is fine)"""
        """ creating a message, not sure if the input argument is enough """
        """ Why pytho don't have switch-case -__- """
        # this method need to be rechecked, since I just do it by using
        # the interface provided by other class
        #
        #
        
        if (messageID = PING_ID):
            body = PingBody(message)
        else if (messageID = PONG_ID):
            body = PongBody(message)
        else if (messageID = QUERY_ID):
            body = QueryBody(message)
        else if (messageID = QUERYHIT_ID):
            body = QueryHitBody(message)
        else if (messageID = PUSH_ID):
            body = PushBody(message)

        ttl = 7
        self.message = Message(7, 0)
        self.message.setBody(body)
        self.reactor = Reactor(self.ip)
        self.reactor.send(peer_id, message)
        
    def OnConnect(self, peerID):
        """ TODO (my part)"""
        """ what to do when a servent connect to a network """

    def OnReceive(self, peerID, message):
        """ TODO (my part) """
        """ servent behavior when receiving a message """

    def OnDisconnect(self, peerID):
        """ TODO (my part) """
        """ servent behavior when leaving the network """

    def OnError(self, peerID):
        """ TODO (my part) """
        """ servent behavior when timeout and/or pause message """

