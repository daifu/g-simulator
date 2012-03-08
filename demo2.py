from pygnutella.network import create_network
from pygnutella.servent import Servent
import sys

def main(args):
    ip = args[0]
    port = int(args[1])
    num_node = int(args[2])
    address = (ip, port)
    create_network([Servent]*num_node, address)

if __name__ == '__main__':
    main(sys.argv[1:])