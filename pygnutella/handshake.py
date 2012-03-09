from context import IContext
from message import Message
import re

HTTP_PATH_VALIDATOR = re.compile('^/get/([0-9]+)/([A-Za-z0-9\\.]+)$') 

class HandShake:
    WELCOME_MESSAGE = 'GNUTELLA CONNECT/0.4\n\n'
    RESPONSE_MESSAGE = 'GNUTELLA OK\n\n'

class HandShakeCompleteContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.handler.reactor.servent.log("handshake completed")
        self.handler.reactor.add_channel(handler)
        self.handler.reactor.servent.on_connect(handler)        
        self.on_read()       
        return
    
    def on_read(self):
        try:
            while True:
                msg = Message()
                msg_length = msg.deserialize(self.handler.received_data)
                if msg_length:
                    self.handler.received_data = self.handler.received_data[msg_length:]
                    self.handler.reactor.servent.on_receive(self.handler, msg)
                else:                    
                    self.handler.reactor.servent.log("message incomplete")
                    break
        except ValueError:
            # The message stream is messed up
            self.handler.reactor.servent.log("Mesage stream is messed up")
            self.handler.handle_close()
            
    def on_close(self):
        # Clean up (i.e. opposite of what we did in __init__)
        self.handler.reactor.servent.on_disconnect(self.handler)
        self.handler.reactor.remove_channel(self.handler)

class HandShakeInContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.on_read()
        return
    
    def on_read(self):
        size = len(HandShake.WELCOME_MESSAGE)
        if len(self.handler.received_data) >= size:
            if HandShake.WELCOME_MESSAGE == self.handler.received_data[:size]:
                self.handler.reactor.servent.log("received Welcome Message")
                if self.handler.reactor.servent.on_accept():
                    self.handler.write(HandShake.RESPONSE_MESSAGE)
                    self.handler.received_data = self.handler.received_data[size:]
                    self.handler.context = HandShakeCompleteContext(self.handler)
                else:
                    self.handler.handle_close()
    
    def on_close(self):
        return

class HandShakeOutContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler, data)
        self.handler.write(HandShake.WELCOME_MESSAGE)
        self.handler.reactor.servent.log("sending Welcome Message")
        self.on_read()
        return
    
    def on_read(self):
        size = len(HandShake.RESPONSE_MESSAGE)
        if len(self.handler.received_data) >= size:
            if HandShake.RESPONSE_MESSAGE == self.handler.received_data[:size]:
                self.handler.reactor.servent.log("received Response Message")
                self.handler.received_data = self.handler.received_data[size:]
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
    DOWNLOAD_INCOMPLETE = 3
    DOWNLOAD_COMPLETE = 4
    BAD_REQUEST = 5
    
class DownloadOutContext(IContext):
    def __init__(self, handler, data):
        IContext.__init__(self, handler)
        self.file_index, self.remote_file_name, self.local_file_name = data
        self.out_file = None
        self.sent_request = False
        try:
            self.out_file = open(self.local_file_name, 'w')
        except IOError:
            self.handle.reactor.servent.on_download(DownloadEventId.BAD_FILE_PATH, self.handler)
            self.handler.handle_close()
            return        
        request = "GET /get/%s/%s/ HTTP/1.0\r\nConnection: Keep-Alive\r\nRange: bytes=0-\r\n\r\n" % (self.file_index, self.remote_file_name)
        self.handler.write(request)
        self.handler.reactor.servent.debug("sending file request")
        self.sent_request = True
        self.got_response = False
        self.num_bytes = 0
        self.max_bytes = 0
        self.on_read()
        return
    
    def on_read(self):
        if not self.got_response and '\r\n\r\n' in self.handler.received_data:
            self.got_response = True
            # getting header of HTTP protocol
            first_index = self.handler.received_data.index('\r\n\r\n')
            self.handler.reactor.serventdebug("received file response")
            header = self.handler.received_data[:first_index].split('\r\n')
            self.handler.received_data = self.handler.received_data[first_index+4:]
            # getting status
            status = header[0].split()[1]
            # Check status
            if int(status) != 200:                
                self.handler.reactor.servent.on_download(DownloadEventId.FILE_NOT_FOUND, self.handler)
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
                self.out_file.close()
                self.handler.reactor.servent.on_download(DownloadEventId.DOWNLOAD_COMPLETE, self.handler)
                self.handler.handle_close()
        return
    
    def on_close(self):
        if self.out_file:
            self.out_file.close()            
        if self.num_bytes == 0 and not self.got_response and self.sent_request:
            self.handler.reactor.servent.on_download(DownloadEventId.CONNECTION_REFUSE, self.handler)
        elif self.num_bytes > 0 and self.num_bytes < self.max_bytes and self.got_response:
            self.handler.reactor.servent.on_download(DownloadEventId.DOWNLOAD_INCOMPLETE, self.handler)        
        return
    
class DownloadInContext(IContext):
    def __init__(self, handler, data=None):
        IContext.__init__(self, handler)
        self.received_request = False
        self.on_read()                       
        return
    
    def on_read(self):
        if not self.received_request and '\r\n\r\n' in self.handler.received_data:
            self.received_request = True
            first_index = self.handler.received_data.index('\r\n\r\n')
            self.handler.reactor.servent.debug("received request")
            header = self.handler.received_data[:first_index].split('\r\n')
            self.handler.received_data = self.handler.received_data[first_index+4:]
            method, path, version = header[0].split()
            if method == "GET" and version == "HTTP/1.0" and HTTP_PATH_VALIDATOR.match(path) is not None:
                self.handler.reactor.servent.debug("request is validated")
                self.file_id, self.file_name = HTTP_PATH_VALIDATOR.split(path)[1:3]
                # Ask servent to get file content for file_id and file_name
                self.file_content = self.handler.reactor.servent.get_file_content(self.file_id, self.file_name)
                if self.file_content:                    
                    size = len(self.file_content)
                    response = "HTTP 200 OK\r\nServer: Gnutella\r\nContent-type: application/binary\r\nContent-length: %s\r\n\r\n" % size
                    self.handler.write(response)
                    self.handler.reactor.servent.log("file found and send response")
                    self.handler.write(self.file_content)
                    self.handler.close_when_done()
                    self.handler.reactor.servent.log("sending content")
                else:
                    bad_response = "HTTP 404 Not Found\r\n\r\n"
                    self.handler.write(bad_response)
                    self.handler.reactor.servent.log("file not found and sending failed response")
                    self.handler.handle_close()
            else:
                self.handler.reactor.servent.on_download(DownloadEventId.BAD_REQUEST, self.handler)
                self.handler.handle_close()
                
    def on_close(self):
        return