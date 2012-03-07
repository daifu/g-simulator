from pygnutella.bootstrap import SimpleBootstrap
from pygnutella.servent import Servent
from pygnutella.scheduler import loop as schedule_loop, close_all
import logging
import sys

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

def main(args):
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
    node_type = args[0].lower()
    if node_type == 'bootstrap':        
        dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
        bootstrap_node = AdvanceBootstrap(dag)
    elif node_type == 'servent':
        ip = args[1]
        port = int(args[2])
        Servent(bootstrap_address = (ip, port))

    try:
        schedule_loop()
    finally:
        close_all()

if __name__ == "__main__":
    main(sys.argv[1:])