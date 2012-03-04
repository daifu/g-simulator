from context import IContext
from message import Message
       
class HandShake:
    WELCOME_MESSAGE = 'GNUTELLA CONNECT/0.4\n\n'
    RESPONSE_MESSAGE = 'GNUTELLA OK\n\n'

class HandShakeCompleteContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.handler.reactor.connector(handler)
        self.handler.reactor.add_channel(handler)
        self.on_read()       
        return
    
    def on_read(self):
        self.logger.debug("on_read()")
        try:
            msg = Message()
            msg_length = msg.deserialize(self.handler.received_data)
            if msg_length:
                self.handler.reactor.receiver(self.handler, msg)
                self.handler.received_data = self.handler.received_data[msg_length:]
            else:
                self.logger.debug("on_read() -> incomplete message")
        except ValueError:
            # The message stream is messed up
            self.logger.debug("on_read() -> mesage stream is messed up")
            self.handler.handle_close()
            
    def on_close(self):
        # Clean up (i.e. opposite of what we did in __init__)
        self.handler.reactor.disconnector(self.handler)
        self.handler.reactor.remove_channel(self.handler)

class HandShakeInContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.on_read()
        return
    
    def on_read(self):
        self.logger.debug("on_read()")
        size = len(HandShake.WELCOME_MESSAGE)
        if len(self.handler.received_data) >= size:
            if HandShake.WELCOME_MESSAGE == self.handler.received_data[:size]:
                self.logger.debug("on_read() got Welcome Message")
                if self.handler.reactor.acceptor():
                    self.handler.write(HandShake.RESPONSE_MESSAGE)
                    self.handler.received_data = self.handler.received_data[size:]
                    self.logger.debug("transit to HandShakeCompleteContext")
                    self.handler.context = HandShakeCompleteContext(self.handler)
                else:
                    self.handler.handle_close()
    
    def on_close(self):
        return

class HandShakeOutContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.handler.write(HandShake.WELCOME_MESSAGE)
        self.logger.debug("sending Welcome Message")
        self.on_read()
        return
    
    def on_read(self):
        self.logger.debug("on_read()")
        size = len(HandShake.RESPONSE_MESSAGE)
        if len(self.handler.received_data) >= size:
            if HandShake.RESPONSE_MESSAGE == self.handler.received_data[:size]:
                self.logger.debug("on_read() got Response Message")
                self.handler.received_data = self.handler.received_data[size:]
                self.logger.debug("transit to HandShakeCompleteContext")
                self.handler.context = HandShakeCompleteContext(self.handler)
            else:
                self.handler.handle_close()
                
    def on_close(self):
        return
    
class ProbeContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.on_read()
        return
        
    def on_read(self):
        self.logger.debug("on_read()")
        if len(self.handler.received_data) >= 3:
            if self.handler.received_data[:3] == "GET":
                self.handler.context = DownloadInContext(self.handler)
            else:
                self.handler.context = HandShakeInContext(self.handler)
    
    def on_close(self):
        return

class DownloadEventId:
    CONNECTION_REFUSE = 0
    FILE_NOT_FOUND = 1
    DOWNLOAD_INCOMPLETE = 2
    DOWNLOAD_COMPLETE = 3
    
class DownloadOutContext(IContext):
    def __init__(self, handler, data):
        IContext.__init__(self, handler, data)
        self.file_index, self.remote_file_name, self.local_file_name = data
        request = "GET /get/%s/%s/ HTTP/1.0\r\nConnection: Keep-Alive\r\nRange: bytes=0-\r\n\r\n" % (self.file_index, self.remote_file_name)
        self.handler.write(request)
        self.logger.debug("sending request")
        self.logger.debug(request)
        self.num_bytes = 0
        self.max_bytes = 0
        self.on_read()
        return
    
    def on_read(self):
        return
    
    def on_close(self):
        if self.num_bytes == 0:
            self.handler.reactor.downloader(DownloadEventId.CONNECTION_REFUSE, self.handler)
        else:
            self.handler.reactor.downloader(DownloadEventId.DOWNLOAD_INCOMPLETE, self.handler)
        return
    
class DownloadInContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)        
        return