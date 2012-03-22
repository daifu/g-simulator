from pygnutella.bootstrap import SimpleBootstrap, BootstrapOutHandler
from pygnutella.scheduler import loop as scheduler_loop, close_all

# This is part I in multi-part series in advance boostrapping
# Implement more advance selecting which node for partner candidate

class AdvanceBootstrap(SimpleBootstrap):
    def get_node(self, exclude=[]):
        # for now it is simple, return all existing node in the system
        ret = [v for v in self.nodes if v not in exclude]            
        return ret

#Expected Output
#Node 1:  [('127.0.1.1', '3435')]
#Node 2:  [('127.0.1.1', '3435'), ('127.0.1.1', '15025')]
#Node 3:  [('127.0.1.1', '3435'), ('127.0.1.1', '15025'), ('127.0.1.1', '1252')]
if __name__ == '__main__':
    bootstrap_node = AdvanceBootstrap()
    node1 = BootstrapOutHandler(('127.0.1.1', 3435), bootstrap_node.addr)
    node2 = BootstrapOutHandler(('127.0.1.1', 15025), bootstrap_node.addr)
    node3 = BootstrapOutHandler(('127.0.1.1', 1252), bootstrap_node.addr)
    try:
        scheduler_loop(count=5)
    finally:
        print "Node 1: ", node1.peer_list
        print "Node 2: ", node2.peer_list
        print "Node 3: ", node3.peer_list
        close_all()