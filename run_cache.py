from pygnutella.servent import FileInfo
from pygnutella.network import create_network
from pygnutella.demo.cache_servent import CacheServent
from pygnutella.scheduler import loop as scheduler_loop, close_all

def usage():
    print "Please run with <bootstrap ip> <bootstrap port> <num of nodes>"

def main():
    # create a network
    # if len(args)<3:
    #     usage();
    #     return
    # ip = args[0]
    # port = int(args[1])
    # num_node = int(args[2])
    # address = (ip, port)
    # create_network([BasicServent]*num_node, address)

    # implement the network
    query_servent = CacheServent()
    query_hit_servent = CacheServent()
    query_hit_servent.set_files([FileInfo(1,"first file", 600),
                                 FileInfo(2,"second file", 2500) ,
                                 FileInfo(3, "third file", 5000)])
    query_hit_servent.reactor.gnutella_connect(query_servent.reactor.address)
    try:
        scheduler_loop(timeout=1,count=10)
    finally:
        #flood is query to neighbors
        query_servent.query_flood('first file')
        scheduler_loop(timeout=1,count=10)
        close_all()



if __name__ == '__main__':
    main()
