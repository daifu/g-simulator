import asyncore, asynchat, socket
from multiprocessing import Process
from scheduler import loop as scheduler_loop, close_all

class SimpleBootstrap(asyncore.dispatcher):
    _nodes = []
    
    def __init__(self, port = 0):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1)
        self.bind((socket.gethostname(), port))
        # get socket address for future use
        self.address = self.socket.getsockname()        
        # listening for incoming connection
        self.listen(5)        
        return
    
    def handle_accept(self):
        sock, _ = self.accept()
        BootstrapInHandler(sock)

    def add_node(self, address):
        self._nodes.append(address)
        
    def get_node(self):
        # return the last join node or empty list if _node is empty
        # override this for more elaborate scheme of bootstrap
        return self._nodes[-2:-1]


class BootstrapMethod:
    """
    This is a list of method with sematic similar to HTTP
    but the protocol is not that complicate
    
    + each message begin with one of following method followed by their parameters
    + each message terminate by a newline
    """
    # GET no parameter
    GET = 'GET'
    # POST <ip> <port> post your node ip and address
    POST = 'POST'
    # PEER <ip> <port> bootstrap return a node with following ip and port
    PEER = 'PEER' 
    # CLOSE signal end of connection
    CLOSE = 'CLOSE'
    
class BootstrapInHandler(asynchat.async_chat):
    def __init__(self, sock, bootstrap):
        asyncore.dispatcher.__init__(self, sock=sock)
        self._bootstrap = bootstrap
        self.set_terminator('\n')
        self._received_data = ''

    def collect_incoming_data(self, data):
        self._received_data += data
    
    def found_terminator(self):
        self.process_message()
    
    def process_message(self):
        tokens = self._received_data.split()
        method = tokens[0]
        args = tokens[1:]
        if method  == BootstrapMethod.POST:
            ip, port = args
            self._bootstrap.add_node((ip, port))
        elif method == BootstrapMethod.GET:
            potential_partners = self._bootstrap.get_node()
            for partner in potential_partners:
                self.push('PEER %s %s\n' % partner)            
            self.push(BootstrapMethod.CLOSE)
            self.close_when_done()
        elif method == BootstrapMethod.CLOSE:
            self.handle_close()
        else:
            raise ValueError
        
class BootstrapOutHandler(asynchat.async_chat):
    def __init__(self, node_address, bootstrap_address):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(bootstrap_address)
        self._node_address = node_address
        self._received_data = ''
        self.peer_list = []
        self.set_terminator('\n')
    
    def handle_connect(self):
        message_params = (BootstrapMethod.POST,) + self.node_address
        self.push('%s %s %s\n' % message_params)
    
    def collect_incoming_data(self, data):
        self._received_data += data
    
    def found_terminator(self):
        self.process_message()
    
    def process_message(self):
        tokens = self._received_data.split()
        method = tokens[0]
        args = tokens[1:]
        if method  == BootstrapMethod.PEER:
            ip, port = args
            self.peer_list.append((ip, port))
        elif method == BootstrapMethod.CLOSE:
            self.handle_close()
        else:
            raise ValueError

def _create_gnutella_node(servent_class, bootstrap_address, files = []):
    servent_class()
    try:
        scheduler_loop()
    finally:
        close_all()

def create_gnutella_network(preferred, bootstrap_cls = SimpleBootstrap):   
    # start up bootstrap node
    bootstrap_node = bootstrap_cls()
    
    # create servent process and pass in prefered servent_class, bootstrap address
    # TODO: add an extra parameter to pass in file list
    for servent_cls in preferred:  
        Process(target = _create_gnutella_node, args=(servent_cls, bootstrap_node.address)).start()

    # run scheduler loop for bootstrap node
    try:
        scheduler_loop()
    finally:
        close_all()