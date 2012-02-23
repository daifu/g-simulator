class IHandShake:
    """
        IHandShake is interface for handshake initial
        part of any protocol
        
        One handshake is created per connection
        
        @var handler: the asyncore connection handler
        
        @var __complete: telling if handshake is complete or not.
        
        @var __success: tell if handshake successfully complete or not
                    
        @var __map: is the attribute map exchange during handshake
    """
    def __init__(self, handler):
        self.handler = handler
        self.__complete = False
        self.__success = False
        self.__map = {}
        return
    
    def complete(self):
        return self.__complete
    
    def success(self):
        return self.__success
    
    def onIncoming(self):
        """
            onIncoming will be called multiple times
            1. Call when receive the first byte comes
            2. Call until complete() return True
        """
        raise NotImplementedError
    
    def onOutgoing(self):
        """
            onOutgoing will be called multiple times
            1. Call when establish TCP connection successfully
            2. Call until complete() return True or connection disconnect
        """
        raise NotImplementedError
    
    def getConnectionAttributeMap(self):
        return self.__map
    
class Gnutella4Handshake(IHandShake):
    """
        Gnutella4Handshake is the handshake for Gnutella version 0.4
    """
    def __init__(self, handler):        
        IHandShake.__init__(self, handler)
        self.__welcome = 'GNUTELLA CONNECT/0.4\n\n'
        self.__response = 'GNUTELLA OK\n\n'
        self.__buffer = ''
        # __map is not inherited from parent, should use map insetead of __map
        #self.__map['version'] = 0.4        
        return
            
    def onIncoming(self):
        self.__buffer = ''
        while True:
            # You cannot read more than len(self.__welcome) if self.__buffer is initially empty
            chunk_size = len(self.__welcome) - len(self.__buffer)
            self.__buffer += self.handler.recv(chunk_size)
            if len(self.__welcome) == len(self.__buffer):
                if self.__buffer == self.__welcome:
                    self.handler.send(self.__response)
                    # TODO: add Servent to add capability of refusing connection
                    self.__complete = True
                    self.__success = True
                else:
                    self.__complete = True
                    self.__success = False
            else:
                yield
        return
    
    def onOutgoing(self):        
        self.handler.send(self.__response)
        yield
        if self.handler.is_closed():
            self.__complete = True
            self.__success = False
            return
        self.__buffer = ''
        while True:
            chunk_size = len(self.__response) - len(self.__buffer)
            self.__buffer += self.handler.recv(chunk_size)
            if len(self.__response) == len(self.__buffer):
                if self.__response == self.__buffer:
                    self.__complete = True
                    self.__success = True
                else:
                    self.__complete = True
                    self.__success = False
            else:
                yield
        return
                
        
        
