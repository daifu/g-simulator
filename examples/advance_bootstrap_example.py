from pygnutella.bootstrap import SimpleBootstrap, BootstrapOutHandler
from pygnutella.scheduler import loop as scheduler_loop, close_all

# This is part II in multi-part series in advance boostrapping
# Implement more advance selecting which node for partner candidate

class AdvanceBootstrap(SimpleBootstrap):
    def __init__(self, dag):
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
        self._dag = dag
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
            pass
        # increase node index
        self._counter += 1
        return ret

# expected output
#Node 1:  []
#Node 2:  [('127.0.1.1', '3435')]
#Node 3:  [('127.0.1.1', '3435')]
#Node 4:  [('127.0.1.1', '15025'), ('127.0.1.1', '1252')]   
if __name__ == '__main__':
    dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
    bootstrap_node = AdvanceBootstrap(dag)
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