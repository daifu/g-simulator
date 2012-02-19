# Servent class
# A node that connecet to other servent node through IP address and
# port number.
#

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
    """** 1 more get and set method for something called sockPool (socketPool) **"""
    """** as Howard want **"""

    def CreateMessage(self, body):
        """ TODO (whoever do it is fine)"""
        """ creating a message, not sure if the input argument is enough """

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

