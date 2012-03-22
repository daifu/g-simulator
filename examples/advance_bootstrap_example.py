from pygnutella.bootstrap import DagBootstrap, BootstrapOutHandler
from pygnutella.scheduler import loop as scheduler_loop, close_all

# expected output
#Node 1:  []
#Node 2:  [('127.0.1.1', '3435')]
#Node 3:  [('127.0.1.1', '3435')]
#Node 4:  [('127.0.1.1', '15025'), ('127.0.1.1', '1252')]   
if __name__ == '__main__':
    dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
    bootstrap_node = DagBootstrap(dag)
    node1 = BootstrapOutHandler(('127.0.1.1', 3435), bootstrap_node.addr)
    node2 = BootstrapOutHandler(('127.0.1.1', 15025), bootstrap_node.addr)
    node3 = BootstrapOutHandler(('127.0.1.1', 1252), bootstrap_node.addr)
    node4 = BootstrapOutHandler(('127.0.1.1', 5682), bootstrap_node.addr)
    try:
        scheduler_loop(count=6)
    finally:
        print "Node 1: ", node1.peer_list
        print "Node 2: ", node2.peer_list
        print "Node 3: ", node3.peer_list
        print "Node 4: ", node4.peer_list
        close_all()