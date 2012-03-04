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
    BAD_FILE_PATH = 2
    DOWNLOAD_INCOMPLETE = 2
    DOWNLOAD_COMPLETE = 3
    
class DownloadOutContext(IContext):
    def __init__(self, handler, data):
        IContext.__init__(self, handler)
        self.file_index, self.remote_file_name, self.local_file_name = data
        self.out_file = None
        self.sent_request = False
        try:
            self.out_file = open(self.local_file_name, 'w')
        except IOError:
            self.handle.reactor.downloader(DownloadEventId.BAD_FILE_PATH, self.handler)
            self.handler.handle_close()
            return        
        request = "GET /get/%s/%s/ HTTP/1.0\r\nConnection: Keep-Alive\r\nRange: bytes=0-\r\n\r\n" % (self.file_index, self.remote_file_name)
        self.handler.write(request)
        self.logger.debug("sending request")
        self.logger.debug(request)
        self.sent_request = True
        self.got_response = False
        self.num_bytes = 0
        self.max_bytes = 0
        self.on_read()
        return
    
    def on_read(self):
        if not self.got_response and self.handler.received_data.count('\r\n\r\n') > 0:
            self.got_response = True
            # getting header of HTTP protocol
            first_index = self.handler.received_data.index('\r\n\r\n')
            self.logger.debug("received response")
            self.logger.debug(self.handler.received_data[:first_index])
            header = self.handler.received_data[:first_index].split('\r\n')
            self.handler.received_data = self.handler.received_data[first_index+4:]
            # getting status
            _, status, _ = header[0].split()
            # Check status
            if int(status) != 200:
                self.handler.reactor.downloader(DownloadEventId.FILE_NOT_FOUND, self.handler)
                self.handler.handle_close()
                return
            # finding Content-length field and extract file size
            for i in xrange(1, len(header)):
                field, value = header[i].split(': ')
                if field == 'Content-Length':
                    self.max_bytes = int(value)                
        if self.got_response:
            # write entire buffer to file
            self.out_file.write(self.handler.received_data)
            # increase number of received byte
            self.num_bytes += len(self.handler.received_data)
            # empty received buffer
            self.handler.received_data = ''
            # if we are at the end of the stream
            if self.num_bytes == self.max_bytes:
                self.logger.debug("Get entire file")
                self.out_file.close()
                self.handler.reactor.downloader(DownloadEventId.DOWNLOAD_COMPLETE, self.handler)
                self.handler.handle_close()
        return
    
    def on_close(self):
        if self.out_file:
            self.out_file.close()            
        if self.num_bytes == 0 and not self.got_response and self.sent_request:
            self.handler.reactor.downloader(DownloadEventId.CONNECTION_REFUSE, self.handler)
        elif self.num_bytes > 0 and self.num_bytes < self.max_bytes and self.got_response:
            self.handler.reactor.downloader(DownloadEventId.DOWNLOAD_INCOMPLETE, self.handler)        
        return
    
class DownloadInContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)        
        return