import sys, logging
from pygnutella.servent import FileInfo
from pygnutella.demo.cache_servent import CacheServent
from pygnutella.scheduler import loop as scheduler_loop, close_all
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.message import create_message

# since CacheServent doesn't have any log
# we need to add our log
class LogCacheServent(CacheServent):
    def save_queryhit(self, message):
        self.log("save in cache %s", message)
        CacheServent.save_queryhit(self, message)
    
    def search_queryhit(self, criteria):
        result = CacheServent.search_queryhit(self, criteria)
        if result:
            self.log("Cache found results(%d)", len(result))
        else:
            self.log("Not in cache")
        return result
    
    def search(self, criteria):
        result = CacheServent.search(self, criteria)
        if result:
            self.log("Servent has the file with name: %s", criteria)
        else:
            self.log("Servent does not have the file")
        return result

def main(args):
    # show log message
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
    # implement the network
    servent1 = LogCacheServent()
    servent2 = LogCacheServent()
    servent3 = LogCacheServent()
    servent4 = LogCacheServent()
    servent5 = LogCacheServent()
    servent3.set_files([FileInfo(1,"first file", 600),
                       FileInfo(2,"second file", 2500) ,
                       FileInfo(3, "third file", 5000)])
    servent1.reactor.gnutella_connect(servent2.reactor.address)
    servent2.reactor.gnutella_connect(servent3.reactor.address)
    servent3.reactor.gnutella_connect(servent4.reactor.address)
    servent5.reactor.gnutella_connect(servent2.reactor.address)
    try:
        print "============Handshake============"
        scheduler_loop(timeout=1,count=10)
    except:
        close_all()
        return
    
    query_message = create_message(GnutellaBodyId.QUERY,
                                   min_speed = 0,
                                   search_criteria = "first file")
    
    # generate two identical query with different message_id
    query_message2 = create_message(GnutellaBodyId.QUERY,
                                   min_speed = 0,
                                   search_criteria = "first file")
            
    try:
        print "============Simulate Query============"
        servent1.flood_ex(query_message)
        scheduler_loop(timeout=1,count=15)
    except:
        close_all()
        return
        
    try:
        print "============Simulate Cache Query============"
        servent5.flood_ex(query_message2)
        scheduler_loop(timeout=1,count=15)
    except:
        close_all()
        return
    
    # clean up
    close_all()
        
if __name__ == '__main__':
    main(sys.argv[1:])