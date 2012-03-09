import logging, random, uuid
from reactor import Reactor
from messagebody import GnutellaBodyId, PongBody
from message import Message

# struct of file, each servent have an array/list of these files
class FileInfo:
    file_id = 0
    file_name =  ""
    # file_size assumed to be in unit of byte
    file_size = 0
    indices = []
    def __init__(self, file_id, file_name, file_size):
        self.indices = file_name.split()
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
   
class BasicServent:
    def __init__(self, port=0, files = [], bootstrap_address = None):
        self._logger = logging.getLogger(self.__class__.__name__ +" "+ str(id(self)))        
        # forwarding table: (message_id, payload_type) -> connection_handler
        self.forwarding_table = {}        
        # create servent id
        self.id = uuid.uuid4().bytes
        self.log("id is %s" % self.id.encode('hex_codec'))
        # calculate number of file and number of kilobyte shared
        self._files = files
        self.num_files = len(files)
        self.num_kilobytes = 0
        for f in files:
            self.num_kilobytes += f.file_size
        self.num_kilobytes /= 1000 # shrink the unit
        # create Reactor class for socket management
        self.reactor = Reactor(self, port)
        # check if bootstrap_address is given
        if bootstrap_address:
            self.reactor.bootstrap_connect(bootstrap_address)        
        return
        
    def on_accept(self):
        """
        on event of gnutella connection, accept or refuse depends on
        resource management
        """
        # Always accept new connection
        return True
    
    def on_connect(self, connection_handler):
        """ 
        on event of a servent connects to 
        """
        return

    def on_receive(self, connection_handler, message):
        """ 
        on event of receiving a message from an existing connection 
        """
        self.log('Receive message from %s', connection_handler.socket.getsockname())

        if message.payload_descriptor == GnutellaBodyId.PING:
            # check if we saw this ping before. If not, then process
            if (message.message_id, GnutellaBodyId.PONG) not in self.forwarding_table:                 
                # send Ping to any neighbor that not the one servent recceived the Ping from
                self.flood(connection_handler, message)
                # add ping to forwarding table to forward PONG
                self.forwarding_table[(message.message_id, GnutellaBodyId.PONG)] = connection_handler
                # reply with Pong (the return trip's ttl should be equals to hops)
                pong_message = Message(message.message_id, message.hops, 0)              
                PongBody(pong_message, self.reactor.ip, self.reactor.port, self.num_files, self.num_kilobytes)
                connection_handler.write(pong_message.serialize())
        elif message._payload_descriptor == GnutellaBodyId.PONG:
            # forwarding pong                 
            self.forward(message)
        elif message.payload_descriptor == GnutellaBodyId.QUERY:
            # check if we saw this query before. If not, then process
            if (message.message_id, GnutellaBodyId.QUERYHIT) not in self.forwarding_table:
                # add to forwarding table to forward QUERYHIT
                self.forwarding_table[(message.message_id, GnutellaBodyId.QUERYHIT)] = connection_handler
                # forward query packet to neighbor servent
                self.flood(connection_handler, message)
        elif message.payload_descriptor == GnutellaBodyId.QUERYHIT:
            # add to forwarding table to forward PUSH
            self.forwarding_table[(message.message_id, message.body.servent_id, GnutellaBodyId.PUSH)] = connection_handler
            # forwarding query hit
            self.forward(message)
        elif message.payload_descriptor == GnutellaBodyId.PUSH:
            if message.body.servent_id == self.id:
                pass
            else:
                # forward push
                self.forward(message)
        else:
            raise ValueError
            
    def on_disconnect(self, connection_handler):
        """ 
        servent behavior when leaving the network 
        """
        self.log('disconnect from the network %s', connection_handler.socket.getsockname())
        # resource clean up
        # clean up forwarding table
        remove = [k for k,v in self.forwarding_table.iteritems() if v == connection_handler]
        for k in remove: 
            del self.forwarding_table[k]
        return
    
    def on_download(self, event_id, connection_handler):
        # DO some logging or resource clean up in here
        return
    
    def on_bootstrap(self, peer_address):
        # connect to all suggested peer
        self.reactor.gnutella_connect(peer_address) 
    
    def log(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)
    
    def forward(self, message):
        """
        Forward message to correct servent in according to forwarding table
        """
        if message.get_ttl() < 2:
            return        
        try:
            message.decrease_ttl()
            packet = message.serialize()
            if message.payload_descriptor != GnutellaBodyId.PUSH:
                self.forwarding_table[(message.message_id, message.payload_descriptor)].write(packet)
            else:
                self.forwarding_table[(message.message_id, message.body.servent_id, message.payload_descriptor)].write(packet)
        except KeyError:
            pass
            
    
    def flood(self, connection_handler, message):
        """
        Flood message to every directly connected servent
        """
        if message.get_ttl() < 2:
            return
        message.decrease_ttl()
        self.reactor.broadcast_except_for(connection_handler, message)
        return
           
    def set_files(self, files):
        # each member of files is a FileInfo 
        self._files = files
        # calculate number of file and number of kilobyte shared
        self.num_files = len(files)
        self.num_kilobytes = 0
        for f in files:
            self.num_kilobytes += f.file_size
        self.num_kilobytes /= 1000 # shrink the unit        
        return

    def get_files(self):
        return self._files

    files = property(get_files, set_files)
    

    def check_file(self, file_id):
        """
        check if the servent have the file with id = file_id
        """
        for fileinfo in self.files:
            if fileinfo.file_id == file_id:
                return True
        return False

    def get_file_content(self, file_id, file_name):
        if not self.check_file(file_id):
            return None
        # return dummy content
        return "This is (%s, %s)" % (file_name, file_id)

    def search(self, criteria):
        """ 
        return a list of file fit the criteria
        """
        tokens = criteria.split()
        match = []
        for t in tokens:
            for fileinfo in self.files:
                if t in fileinfo.indices:
                    match.append(fileinfo)                       
        return match
    
    
class RandomWalkServent(BasicServent):
    """
    This servent when flood, send with probability 0.5
    """
    def flood(self, connection_handler, message):
        if message.get_ttl() < 2:
            return
        message.decrease_ttl()
        packet = message.serialize()
        for handler in self.reactor.channels:
            if not handler == connection_handler:
                if random.randint(0, 10) & 1:
                    handler.write(packet)

class SilentServent(BasicServent):
    def log(self, msg, *args, **kwargs):
        # Do nothing i.e. silent the output
        pass