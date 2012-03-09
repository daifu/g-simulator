from pygnutella.network import create_network
from pygnutella.servent import BasicServent
import sys

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
    create_network([BasicServent]*num_node, address)

if __name__ == '__main__':
    main(sys.argv[1:])