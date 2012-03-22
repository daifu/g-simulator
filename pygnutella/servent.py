import logging, uuid, copy, time
from numpy.random import binomial
from reactor import Reactor
from messagebody import GnutellaBodyId
from message import create_message

# struct of file, each servent have an array/list of these files
class FileInfo:
    def __init__(self, file_id, file_name, file_size):
        self.indices = file_name.split()
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        
    def get_result_set(self):
        return {
                "file_index": self.file_id,
                "file_name": self.file_name,
                "file_size": self.file_size
                }

class BasicServent:
    """
    This class implements everything that a Servent "must do" as part of Gnutella 0.4 protocol
    
    To add more feature, simply derive this. You can either override entire method or
    add more functionality by implement it and then add parent's method.
    """
    # Fixed expiration period  per ttl in unit of second
    FIXED_EXPIRED_INTERVAL = 5
    def __init__(self, port=0, files = [], bootstrap_address = None):
        self._logger = logging.getLogger("%s(%s)" % (self.__class__.__name__, hex(id(self))[:-1]))        
        # forwarding table: (message_id, payload_type) -> (connection_handler,
        # expiration)
        self.forwarding_table = {}
        # flood/forward ignore table: message_id -> timestamp
        # this table used to prevent loop in flood
        # all message send out need to put their message_id and
        # timestamp = time.time()+ttl*FIXED_EXPIRED_INTERVAL
        self.ignore = {}
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
        if message.payload_descriptor == GnutellaBodyId.PING:
            # check if we saw this ping before. If not, then process
            forward_key = (message.message_id, GnutellaBodyId.PONG)
            now = time.time()
            not_seen_or_expire = forward_key not in self.forwarding_table or (self.forwarding_table[forward_key][1] < now)
            not_ignore_or_expire = message.message_id not in self.ignore or (self.ignore[message.message_id] < now) 
            if  not_seen_or_expire and not_ignore_or_expire:                                 
                # send Ping to any neighbor that not the one servent recceived the Ping from
                self.flood(connection_handler, message)
                # add ping to forwarding table to forward PONG
                self.put_into_forwarding_table(message, connection_handler)
                # reply with Pong (the return trip's ttl should be equals to hops)
                pong_message = create_message(GnutellaBodyId.PONG, 
                                              message.message_id, 
                                              message.hops+1,
                                              ip = self.reactor.ip,
                                              port = self.reactor.port,
                                              num_of_files = self.num_files,
                                              num_of_kb = self.num_kilobytes)
                self.log("Sending replied pong %s", pong_message)
                self.send_message(pong_message, connection_handler)
        elif message.payload_descriptor == GnutellaBodyId.PONG:
            # forwarding pong                 
            self.forward(message)
        elif message.payload_descriptor == GnutellaBodyId.QUERY:
            # check if we saw this query before. If not, then process
            forward_key = (message.message_id, GnutellaBodyId.QUERYHIT)
            now = time.time()
            not_seen_or_expire = forward_key not in self.forwarding_table or (self.forwarding_table[forward_key][1] < now)
            not_ignore_or_expire = message.message_id not in self.ignore or (self.ignore[message.message_id] < now)             
            if not_seen_or_expire and not_ignore_or_expire:
                # add to forwarding table to forward QUERYHIT
                self.put_into_forwarding_table(message, connection_handler)
                # forward query packet to neighbor servent
                self.flood(connection_handler, message)
        elif message.payload_descriptor == GnutellaBodyId.QUERYHIT:
            # don't route query hit if it is meant for this node            
            if not message.body.servent_id == self.id:
                # forwarding query hit
                if self.forward(message):
                    # add to forwarding table to forward PUSH
                    self.put_into_forwarding_table(message, connection_handler)                
        elif message.payload_descriptor == GnutellaBodyId.PUSH:
            # don't route push if it is meant for this node
            if not message.body.servent_id == self.id:
                # forward push
                self.forward(message)                
        else:
            raise ValueError('message type is not one of PING, PONG, QUERY, QUERYHIT, PUSH')
            
    def on_disconnect(self, connection_handler):
        """ 
        servent behavior when leaving the network 
        """
        # resource clean up
        # clean up forwarding table
        remove = [k for k,v in self.forwarding_table.iteritems() if v[0] == connection_handler]
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
    
    def send_message(self, message, handler):
        """
        Servent sends its own message (not as part of flood / forwarding)
        
        By using this method, Servent can keep track which message (by message_id) is its own
        by adding it to ignore dictionary.
        """
        self.ignore[message.message_id] = time.time()+self.FIXED_EXPIRED_INTERVAL*message.ttl
        handler.write(message.serialize())
    
    def put_into_forwarding_table(self, message, handler):
        now = time.time()
        message_id = copy.deepcopy(message.message_id)
        value = (handler, now+self.FIXED_EXPIRED_INTERVAL*message.ttl)
        key = None
        if message.payload_descriptor == GnutellaBodyId.QUERYHIT:
            key = (message_id, message.body.servent_id, GnutellaBodyId.PUSH)            
            self.forwarding_table[key] = value
        elif message.payload_descriptor == GnutellaBodyId.PING:
            key = (message_id, GnutellaBodyId.PONG)
            self.forwarding_table[key] = value
        elif message.payload_descriptor == GnutellaBodyId.QUERY:
            key = (message_id, GnutellaBodyId.QUERYHIT)        
        else:
            raise ValueError
        # insert into forwarding table
        self.forwarding_table[key] = value
        
    
    def forward(self, message):
        """
        Forward message to correct servent in according to forwarding table
        """
        if message.ttl < 2:
            return False        
        try:
            # create a deep copy
            message = copy.deepcopy(message)
            message.decrease_ttl()
            packet = message.serialize()
            key = None
            if message.payload_descriptor != GnutellaBodyId.PUSH:
                key = (message.message_id, message.payload_descriptor)
            else:
                key = (message.message_id, message.body.servent_id, message.payload_descriptor)            
            handler, timestamp = self.forwarding_table[key]
            if time.time() < timestamp:
                handler.write(packet)
                return True
            else:
                self.log("forwarding timestamp expired -> %s", message)
                del self.forwarding_table[key]
            return False
        except KeyError:
            return False
        return False 
            
    
    def flood(self, received_handler, message):
        """
        Flood other servent's message to every directly connected servent other
        than the received handler. This method is used as part of forwarding of ping, query
        
        return number of connection is flooded
        """
        if message.ttl < 2:
            return 0
        # create a deep copy
        message = copy.deepcopy(message)        
        message.decrease_ttl()
        return self.reactor.broadcast_except_for(received_handler, message)

    def flood_ex(self, message):
        """
        Flood your own message to every directly connected servent

        return number of connection is flooded
        """
        # you can only flood query or ping message by definition of protocol
        if message.payload_descriptor == GnutellaBodyId.QUERY or message.payload_descriptor == GnutellaBodyId.PING:
            self.ignore[message.message_id] = time.time()+self.FIXED_EXPIRED_INTERVAL*message.ttl
            return self.reactor.broadcast_except_for(None, message)
        return 0
           
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
        Return a list of file fit the criteria
        Exact match for file name
        """
        match = []
        for fileinfo in self.files:
            if criteria == fileinfo.file_name:
                match.append(fileinfo)
        return match
    
    
class RandomWalkServent(BasicServent):
    """
    This servent when flood, send with probability 0.5
    """
    def flood(self, connection_handler, message):
        if message.ttl < 2:
            return
        message.decrease_ttl()
        packet = message.serialize()
        for handler in self.reactor.channels:
            if not handler == connection_handler:
                if binomial(1, 0.5) == 1:
                    handler.write(packet)

class SilentServent(BasicServent):
    def log(self, msg, *args, **kwargs):
        # Do nothing i.e. silent the output
        pass
