from pygnutella.network import create_network
from pygnutella.demo.log_servent import LogServent
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.message import create_message
import sys

class ExampleServent(LogServent):
    def on_connect(self, connection_handler):
        LogServent.on_connect(self, connection_handler)
        ping_message = create_message(GnutellaBodyId.PING)
        self.log("sending %s", ping_message)
        self.send_message(ping_message, connection_handler)               
        
def usage():
    print "Please run with <bootstrap ip> <bootstrap port> <num of nodes>"

def main(args):
    if len(args)<3:
        usage();
        return
    ip = args[0]
    port = int(args[1])
    num_node = int(args[2])
    address = (ip, port)
    create_network([ExampleServent]*num_node, address)

if __name__ == '__main__':
    main(sys.argv[1:])