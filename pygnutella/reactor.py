import asyncore
import socket
import re
import utils
from bootstrap import BootstrapOutHandler
from message import Message

class Reactor:
    """
        Reactor is socket management class using Reactor Design Pattern
        User should not make more than one instance of Reactor.
        
        3 Steps to use the class:
        
        1. Initialization:
        reactor = Reactor(servent)
                        
        2. Event Loop:
        asyncore.loop()
        
        OR
        
        scheduler.loop()        
    """
    
    def __init__(self, servent, port = 0):
        self.servent = servent
        self.channels = []
        self.server_handler = GnutellaServer(reactor = self, port = port)        
        return
        
    def broadcast_except_for(self, handler, message):
        packet = message.serialize()
        for connection_handler in self.channels:
            if not connection_handler == handler:
                connection_handler.write(packet)
        return
    
    def add_channel(self, handler):     
        self.channels.append(handler)
        return
    
    def remove_channel(self, handler):      
        try:                
            self.channels.remove(handler)
        except ValueError:
            pass        
        
    def gnutella_connect(self, address):
        self.servent.log("gnutella_connect() -> %s %s" % address)
        try:
            GnutellaClientHandler(self, address)
        except socket.error:
            self.servent.log("failed to connect")
            return False 
        return True
    
    def download_connect(self, address, remote_file_index, remote_file_name, local_file_name):
        self.servent.log("download_connect() -> %s %s" % address)
        try:
            DownloadClientHandler(self, 
                                  remote_file_index, 
                                  remote_file_name, 
                                  local_file_name, address)
        except socket.error:
            self.servent.log("failed to connect")
            return False 
        return True
    
    def bootstrap_connect(self, address):
        self.servent.log('bootstrap_connect() -> %s %s' % address)
        try:
            self.bootstrap_handler = BootstrapOutHandler(node_address = self.address, 
                                                         bootstrap_address = address, 
                                                         servent = self.servent)
        except socket.error:
            self.servent.log("failed to connect")
            return False
        return True

class GnutellaServer(asyncore.dispatcher):
    """
        This is the GnutellaServer which is to handle incoming connections.        
    """
    def __init__(self, reactor, port):       
        self.reactor = reactor
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1
        self.bind((socket.gethostname(), port))
        # get socket address for future use
        self.reactor.address = self.socket.getsockname()
        self.reactor.ip = utils.dotted_quad_to_num(self.reactor.address[0])
        self.reactor.port = self.reactor.address[1]        
        self.reactor.servent.log('bind to %s %s' % self.reactor.address)
        # listening for incoming connection
        self.listen(5)
        return
    
    def handle_accept(self):
        sock, _ = self.accept()
        self.reactor.servent.log('tcp connection established')
        ServerHandler(self.reactor, sock=sock)
        return
    
    def handle_close(self):
        self.close()
        self.reactor.server_handler = None     
        return
    
class ConnectionHandler(asyncore.dispatcher):
    """
        This is a generic handler for connection either incoming or outgoing.
        
        Derive this class hook process_read()
    """    
    def __init__(self, reactor, chunk_size=512, close_when_done = False):        
        self._data_to_write = ''
        self.received_data = ''
        self.process_read = None
        self.reactor = reactor
        self.chunk_size = chunk_size
        self._close_when_done = close_when_done
        asyncore.dispatcher.__init__(self)
        return
        
    def write(self, data):
        self._data_to_write += data
        return
                
    def writable(self):            
        response = bool(self._data_to_write)
        return response
        
    def handle_close(self):
        self.reactor.servent.log('handle_close()')       
        self.close()  
        return
    
    def handle_read(self):
        #self.reactor.servent.log("handle_read() -> %s", self._context)
        self.received_data += self.recv(self.chunk_size)
        if callable(self.process_read):
            self.process_read()
        else:
            self.reactor.servent.log("process_read() is not callable")
        return
    
    def trim_buffer(self, length):
        self.received_data = self.received_data[length:]
    
    def handle_write(self):
        """
            Write as much as possible
        """
        sent = self.send(self._data_to_write)
        #self.reactor.servent.log("handle_write() -> to: %s buffer: %d sent: %d", self.socket.getpeername(), len(self._data_to_write), sent)        
        self._data_to_write = self._data_to_write[sent:]
        # check flag: close_after_last_write
        if self._close_when_done and not self.writable():
            self.reactor.servent.log("close_when_done()")
            self.handle_close()
        return
    
    def close_when_done(self):
        self._close_when_done = True

class HandShake:
    # handshake for 0.4 gnutella
    WELCOME_MESSAGE = 'GNUTELLA CONNECT/0.4\n\n'
    WELCOME_MESSAGE_LEN = len(WELCOME_MESSAGE)
    OK_MESSAGE = 'GNUTELLA OK\n\n'
    OK_MESSAGE_LEN = len(OK_MESSAGE)
    # download
    HTTP_GET = 'GET'
    GNUTELLA_CONNECT = 'GNUTELLA CONNECT'
    HTTP_GET_LEN = len(HTTP_GET)
    GNUTELLA_CONNECT_LEN = len(GNUTELLA_CONNECT)
    
HTTP_PATH_VALIDATOR = re.compile('^/get/([0-9]+)/([A-Za-z0-9\\.]+)$')

class DownloadEventId:
    CONNECTION_REFUSE = 0
    FILE_NOT_FOUND = 1
    BAD_FILE_PATH = 2
    DOWNLOAD_INCOMPLETE = 3
    DOWNLOAD_COMPLETE = 4
    BAD_REQUEST = 5 


class ServerHandler(ConnectionHandler):    
    def __init__(self, reactor, sock):
        ConnectionHandler.__init__(self, reactor)
        sock.setblocking(False)
        self.set_socket(sock)
        self.process_read = self._probe
        self._handshake_complete = False
        self._received_download_request = False
        
    def _probe(self):
        if (len(self.received_data) >= HandShake.HTTP_GET_LEN 
            and self.received_data[:HandShake.HTTP_GET_LEN] == HandShake.HTTP_GET):
            # swap to download handler
            self.process_read = self._download
            self.process_read()
        elif (len(self.received_data) >= HandShake.GNUTELLA_CONNECT_LEN 
              and self.received_data[:HandShake.GNUTELLA_CONNECT_LEN] == HandShake.GNUTELLA_CONNECT):
            # swap to handshake handler
            self.process_read = self._handshake
            self.process_read()
        else:
            self.reactor.servent.log("probe failed i.e. not expected connection")
            self.handle_close()        
    
    def _handshake(self):
        if len(self.received_data) >= HandShake.WELCOME_MESSAGE_LEN:
            if HandShake.WELCOME_MESSAGE == self.received_data[:HandShake.WELCOME_MESSAGE_LEN]:
                self.reactor.servent.log("received welcome")
                # remove welcome message from buffer
                self.trim_buffer(HandShake.WELCOME_MESSAGE_LEN)
                if self.reactor.servent.on_accept():
                    self.reactor.servent.log("sending ok")
                    self.write(HandShake.OK_MESSAGE)
                    # initialize after handshake, set flag for
                    # deallocate later
                    self._handshake_complete = True
                    self.reactor.add_channel(self)
                    self.reactor.servent.on_connect(self)                  
                    # swap to gnutella handler
                    self.process_read = self._gnutella
                    # run to check if we miss any message
                    self.process_read()                    
                else:
                    self.handle_close()
        pass
    
    def _gnutella(self):
        try:
            while True:
                msg = Message()
                msg_length = msg.deserialize(self.received_data)
                if msg_length:
                    self.received_data = self.received_data[msg_length:]
                    self.reactor.servent.on_receive(self, msg)
                else:                    
                    self.reactor.servent.log("decoding -> message incomplete")
                    break
        except ValueError:
            # The message stream is messed up
            self.reactor.servent.log("Mesage stream is messed up")
            self.handle_close()        
                
    def _download(self):
        if not self._received_download_request and '\r\n\r\n' in self.received_data:
            self._received_download_request = True
            first_index = self.received_data.index('\r\n\r\n')
            self.reactor.servent.debug("received download request")
            header = self.received_data[:first_index].split('\r\n')
            # remove HTTP request from buffer
            self.trim_buffer(first_index+4)
            # get the request
            method, path, version = header[0].split()
            if method == "GET" and version == "HTTP/1.0" and HTTP_PATH_VALIDATOR.match(path) is not None:
                self.reactor.servent.debug("request is validated")
                self.file_id, self.file_name = HTTP_PATH_VALIDATOR.split(path)[1:3]
                # Ask servent to get file content for file_id and file_name
                self.file_content = self.reactor.servent.get_file_content(self.file_id, self.file_name)
                if self.file_content:                    
                    file_size = len(self.file_content)
                    response = ["HTTP 200 OK",
                                "Server: Gnutella",
                                "Content-type: application/binary",
                                "Content-length: %d" % file_size]
                    self.write(response.join("\r\n")+"\r\n\r\n")
                    self.reactor.servent.log("file found and sending response")
                    self.write(self.file_content)
                    self.close_when_done()
                    self.reactor.servent.log("sending content")
                else:
                    bad_response = "HTTP 404 Not Found\r\n\r\n"
                    self.write(bad_response)
                    self.reactor.servent.log("file not found and sending failed response")
                    self.handle_close()
            else:
                self.reactor.servent.on_download(DownloadEventId.BAD_REQUEST, self)
                self.handle_close()    
    
    def handle_close(self):
        ConnectionHandler.handle_close(self)
        if self._handshake_complete:
            # clean up
            self.reactor.servent.on_disconnect(self)
            self.reactor.remove_channel(self)  
    
class GnutellaClientHandler(ConnectionHandler):
    def __init__(self, reactor, address):
        ConnectionHandler.__init__(self, reactor)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address)
        self.process_read = self._handshake
        self._handshake_complete = False
        self.reactor.servent.log("sending welcome")
        self.write(HandShake.WELCOME_MESSAGE)
        
    def _handshake(self):
        if len(self.received_data) >= HandShake.OK_MESSAGE_LEN:
            if HandShake.OK_MESSAGE == self.received_data[:HandShake.OK_MESSAGE_LEN]:
                self.reactor.servent.log("received ok")
                # remove ok message from buffer
                self.trim_buffer(HandShake.OK_MESSAGE_LEN)
                # initialize after handshake, set flag for
                # deallocate later
                self._handshake_complete = True
                self.reactor.add_channel(self)
                self.reactor.servent.on_connect(self)                  
                # swap to gnutella handler
                self.process_read = self._gnutella
                # run to check if we miss any message
                self.process_read()
            else:
                self.handle_close()        
    
    def _gnutella(self):
        try:
            while True:
                msg = Message()
                msg_length = msg.deserialize(self.received_data)
                if msg_length:
                    self.received_data = self.received_data[msg_length:]
                    self.reactor.servent.on_receive(self, msg)
                else:                    
                    self.reactor.servent.log("decoding -> message incomplete")
                    break
        except ValueError:
            # The message stream is messed up
            self.reactor.servent.log("Mesage stream is messed up")
            self.handle_close()
    
    def handle_close(self):
        ConnectionHandler.handle_close(self)
        if self._handshake_complete:
            # clean up
            self.reactor.servent.on_disconnect(self)
            self.reactor.remove_channel(self)           

   
class DownloadClientHandler(ConnectionHandler):
    def __init__(self, reactor, address, remote_file_index, remote_file_name, local_file_name):
        ConnectionHandler.__init__(self, reactor)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address)
        # swap in init handler
        self.process_read = self._download
        self._remote_file_index = remote_file_index
        self._remote_file_name = remote_file_name
        self._local_file_name = local_file_name        
        self.out_file = None
        self._sent_request = False        
        try:
            self.out_file = open(self.local_file_name, 'w')
        except IOError:
            self.reactor.servent.on_download(DownloadEventId.BAD_FILE_PATH, self)
            self.handle_close()
        request = ["GET /get/%s/%s/ HTTP/1.0" % (self._remote_file_index, self._remote_file_name),
                   "Connection: Keep-Alive",
                   "Range: bytes=0-"]        
        self.write(request.join("\r\n") + "\r\n\r\n")
        self.reactor.servent.log("sending file request")
        self._sent_request = True
        self._got_response = False
        self.num_bytes = 0
        self.max_bytes = 0
                                
    def _download(self):
        if not self._got_response and '\r\n\r\n' in self.received_data:
            # set flag
            self._got_response = True
            # getting header of HTTP protocol
            first_index = self.received_data.index('\r\n\r\n')
            self.reactor.serventdebug("received file response")
            header = self.received_data[:first_index].split('\r\n')
            # remove HTTP response header from buffer
            self.trim_buffer(first_index+4)
            # getting status
            status = header[0].split()[1]
            # Check status
            if int(status) != 200:                
                self.reactor.servent.on_download(DownloadEventId.FILE_NOT_FOUND, self)
                self.handle_close()
                return
            # finding Content-length field and extract file size
            for i in xrange(1, len(header)):
                field, value = header[i].split(': ')
                if field == 'Content-Length':
                    self.max_bytes = int(value)                
        if self._got_response:
            # write entire buffer to file
            self.out_file.write(self.received_data)
            # increase number of received byte
            self.num_bytes += len(self.received_data)
            # empty received buffer
            self.trim_buffer(len(self.received_data))
            # if we are at the end of the stream
            if self.num_bytes == self.max_bytes:
                self.out_file.close()
                self.reactor.servent.on_download(DownloadEventId.DOWNLOAD_COMPLETE, self)
                self.handle_close()

    def handle_close(self):
        ConnectionHandler.handle_close(self)
        if self.out_file:
            self.out_file.close()
        if self.num_bytes == 0 and not self._got_response and self._sent_request:
            self.reactor.servent.on_download(DownloadEventId.CONNECTION_REFUSE, self)
        elif self.num_bytes > 0 and self.num_bytes < self.max_bytes and self._got_response:
            self.reactor.servent.on_download(DownloadEventId.DOWNLOAD_INCOMPLETE, self)        
        return