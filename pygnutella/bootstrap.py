import asyncore
import asynchat
import socket
import logging
from numpy.random import binomial, randint

class SimpleBootstrap(asyncore.dispatcher):
    """
    A new node simply connects to the last node posted ip/addr
    
    example:
    python run_bootstrap.py SimpleBootstrap
    """
    
    def __init__(self):
        self.nodes = []
        self.logger = logging.getLogger(self.__class__.__name__) 
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1)
        self.bind((socket.gethostname(), 0))
        # get socket address for future use
        self.addr = self.socket.getsockname()
        self.logger.info("address at %s %s" % (self.addr))        
        # listening for incoming connection
        self.listen(5)
        return
    
    def handle_accept(self):
        sock, _ = self.accept()
        BootstrapInHandler(sock, self)

    def add_node(self, address):
        self.nodes.append(address)

    @staticmethod
    def parse(argv):
        """
        This method is use to parse argv from command line
        to create parameter for constructor for the class
        """
        return {}
        
    def get_node(self):
        # return the last join node or empty list if _node is empty
        # override this for more elaborate scheme of bootstrap
        return self.nodes[-2:-1]


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
        asynchat.async_chat.__init__(self, sock=sock)
        self._bootstrap = bootstrap
        self.set_terminator('\n')
        self._received_data = ''

    def collect_incoming_data(self, data):
        self._received_data += data
    
    def found_terminator(self):
        self.process_message()
    
    def process_message(self):
        self._bootstrap.logger.info("receive %s", self._received_data)
        tokens = self._received_data.split()
        method = tokens[0]
        args = tokens[1:]
        if method  == BootstrapMethod.POST:
            ip, port = args
            self._bootstrap.add_node((ip, port))
        elif method == BootstrapMethod.GET:
            potential_partners = self._bootstrap.get_node()
            for partner in potential_partners:
                self._bootstrap.logger.info("sent %s %s" % partner)
                self.push('PEER %s %s\n' % partner)            
            self.push("%s\n" % BootstrapMethod.CLOSE)
            self.close_when_done()
        elif method == BootstrapMethod.CLOSE:
            self.handle_close()
        else:
            raise ValueError
        # clean the buffer
        self._received_data = ''
        
class BootstrapOutHandler(asynchat.async_chat):
    def __init__(self, node_address, bootstrap_address, servent = None):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(bootstrap_address)
        self._node_address = node_address
        self._servent = servent
        self._received_data = ''
        self.peer_list = []
        self.set_terminator('\n')
    
    def handle_connect(self):
        message_params = (BootstrapMethod.POST,) + self._node_address
        self.push('%s %s %s\n' % message_params)
        self.push("%s\n" % BootstrapMethod.GET)
    
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
            address = (ip, int(port))
            self.peer_list.append(address)
            if self._servent:
                self._servent.on_bootstrap(address)            
        elif method == BootstrapMethod.CLOSE:
            self.handle_close()
        else:
            raise ValueError
        # clean the buffer
        self._received_data = ''    
        
class DagBootstrap(SimpleBootstrap):
    """
    This is DAG (directly asyclic graph) bootstrap.
    You can pass in a DAG to tell how the node connects to each
    other initially.
    
    An adjacent list is specified as follow
    + a semi-colon denote separation list
    + a colon than sign denote mapping
    + a coma denote separation of node inside a list, but not last node
    + space is not important
    + order is not important
    + repetition will result in override and last copy is the list\n\
    
    example: 
    python run_bootstrap.py DagBootstrap 3 : 1, 2; 1:0; 2:1,0; 3: 0
    
    result in
    Adjacency list {1: [0], 2: [1,0], 3: [0]}    
    """
    def __init__(self, dag=[]):
        SimpleBootstrap.__init__(self)
        # first node is zero
        self._counter = 0
        # this is DAG graph represent in adjacent list dictionary
        # example:
        # dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
        # node 0 -> empty, because first node always zero
        # node 1 -> node 0
        # node 2 -> node 0, also could include node 1 too
        # node 3 -> node 1, node 2
        # parameter check
        for k in dag.keys():
            self._dag = [i for i in dag[k] if i < k and i >= 0]
        self.logger.debug("Dag: " + self._dag)
        
    def get_node(self):
        ret = []
        try:
            adj_list = self._dag[self._counter]
            for node_index in adj_list:
                try:
                    ret.append(self.nodes[node_index])
                except IndexError:
                    pass
        except KeyError:
            # if there is no node, return the last connect node
            # the default behavior
            return SimpleBootstrap.get_node(self)
        # increase node index
        self._counter += 1
        return ret
    
    @staticmethod
    def parse(argv):
        """
        This method is use to parse argv from command line
        to create parameter for constructor for the class
        """
        arg = "".join(argv)
        return {}    
    
class RandomBootstrap(SimpleBootstrap):
    """
    example: 
    for p = 0.7, 
    
    python run_bootstrap.py RandomBootstrap 0.7
    """
    def __init__(self, p):
        """
        p is a probability of selecting a node
        """
        SimpleBootstrap.__init__(self)
        if p >= 1.:
            self.logger.debug("p is larger than or equal to 1, change p to 0.5")
            p = 0.5
        self._p = p
        self.logger.debug("p is %s", self._p)
        
    def get_node(self):
        if len(self.nodes) < 2:
            return []
        ret = []
        # don't get the last node, because it is the current node
        for x in xrange(0,len(self.nodes)-1):
            if binomial(1, self._p) == 1:
                ret.append(self.nodes[x])
        # check to see if it is empty
        if not ret:
            # using default behavior
            return [self.nodes[randint(0, len(self.nodes)-1)]]
        # if not empty, return the node
        return ret

    @staticmethod
    def parse(argv):
        """
        This method is use to parse argv from command line
        to create parameter for constructor for the class
        """
        p = float(argv[0])
        return {'p': p}   
            