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
