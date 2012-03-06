import asyncore, socket
from servent import Servent
from multiprocessing import Process, Pipe
from scheduler import loop as scheduler_loop

_nodes = []

class Bootstrap(asyncore.dispatcher):
    def __init__(self, port = 0):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to a public ip (not localhost or 127.0.0.1
        self.bind((socket.gethostname(), port))
        # get socket address for future use
        self.ip, self.port = self.socket.getsockname()        
        # listening for incoming connection
        self.listen(5)        
        return
    
    def handle_accept(self):
        sock, _ = self.accept()
        BootstrapHandler(sock)

class BootstrapHandler(asyncore.dispatcher):
    def __init__(self, sock, chunk_size = 512):
        asyncore.dispatcher.__init__(self, sock=sock)
        self.chunk_size = chunk_size
        self._data_to_write = ''
        self.received_data = ''
        
    def write(self, data):
        self._data_to_write += data
        return
            
    def writable(self):        
        response = bool(self._data_to_write)       
        return response
    
    def handle_read(self):
        self.received_data += self.recv(self.chunk_size)
        while '\n' in self.received_data:
            self.process_command()
        return
    
    def process_command(self):
        index_found = self.received_data.index('\n')
        raw_command = self.received_data[:index_found]
        self.received_data = self.received_data[index_found:]
        command = deconstruct_command(raw_command)
        if command.cmd == Command.CONNECT:
            # TODO implement process command
            pass
        return
        
     

class Command:
    """
    This is a list of command send from "bootstrap" process
    to other process for setup.
    """
    # connect command have following ip and port
    # CONNECT 127.0.1.1 8934
    CONNECT = "CONNECT"
    START = "START"
    ON = "ON"
    INFO = "INFO"

class Event:
    """
    This is a list of event
    
    All event log begin with ON <event> <other parameters>
    """
    # example
    # ON LISTENNING <id-hex-string> 127.0.1.1 8945
    LISTENING = "LISTENNING"
    RECEIVED = "RECEIVED"


def construct_command(cmd, **kwargs):
    if cmd == Command.CONNECT:
        return "%s %s %s" % (Command.CONNECT, kwargs['ip'], kwargs['port'])
    elif cmd == Command.START:
        return Command.START
    else:
        raise ValueError

def deconstruct_command(raw_cmd):
    tokens = raw_cmd.split()
    cmd = tokens[0]
    if cmd == Command.CONNECT:
        return {'command': cmd, 'ip': tokens[1], 'port': tokens[2]}
    return None

def create_gnutella_node(servent_class, pipe, files):
    servent = servent_class()
    # TODO: fixed this
    pipe.send('ON LISTENNING %s %s %s' % ('myhex_id', '127.0.1.1', '3945'))
    # TODO: receiving peer list
    while True:
        cmd = pipe.recv()        
        if cmd == 'START':
            break
        else:
            # TODO process command
            pass        
    scheduler_loop()
    pipe.close()

def create_gnutella_network(num_nodes = 10, adjacent_list, preferred_list = []):
    for _ in xrange(num_nodes):
        parent_conn, child_conn = Pipe()
        p = Process(target = create_gnutella_node, args=(Servent, child_conn,)).start()
