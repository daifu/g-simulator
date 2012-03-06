from pygnutella.bootstrap import create_gnutella_network
from pygnutella.servent import Servent

if __name__ == '__main__':
    # create ten basic servent wit basic bootstrap
    create_gnutella_network([Servent]*2);
