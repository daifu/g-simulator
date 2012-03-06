from pygnutella.bootstrap import SimpleBootstrap, BootstrapOutHandler
from pygnutella.scheduler import loop as scheduler_loop, close_all

# You should see the following or something like this if you get PYTHONPATH fixed
# explanation: the first message => request from node with port=38383
# bootstrap node with port = 36124
#('127.0.0.1', 38383)  ->  ('127.0.1.1', 36124) POST 127.0.1.1 3435
#('127.0.0.1', 38383)  ->  ('127.0.1.1', 36124) GET
#('127.0.0.1', 38384)  ->  ('127.0.1.1', 36124) POST 127.0.1.1 15025
#('127.0.0.1', 38384)  ->  ('127.0.1.1', 36124) GET
#('127.0.1.1', 36124)  ->  ('127.0.0.1', 38383) CLOSE
#('127.0.1.1', 36124)  ->  ('127.0.0.1', 38384) PEER 127.0.1.1 3435
#('127.0.1.1', 36124)  ->  ('127.0.0.1', 38384) CLOSE
#('127.0.0.1', 38385)  ->  ('127.0.1.1', 36124) POST 127.0.1.1 1252
#('127.0.0.1', 38385)  ->  ('127.0.1.1', 36124) GET
#('127.0.1.1', 36124)  ->  ('127.0.0.1', 38385) PEER 127.0.1.1 15025
#('127.0.1.1', 36124)  ->  ('127.0.0.1', 38385) CLOSE
#Node 1:  []
#Node 2:  [('127.0.1.1', '3435')]
#Node 3:  [('127.0.1.1', '15025')]

if __name__ == '__main__':
    bootstrap_node = SimpleBootstrap()
    node1 = BootstrapOutHandler(('127.0.1.1', 3435), bootstrap_node.address)
    node2 = BootstrapOutHandler(('127.0.1.1', 15025), bootstrap_node.address)
    node3 = BootstrapOutHandler(('127.0.1.1', 1252), bootstrap_node.address)
    try:
        scheduler_loop(count=5)
    finally:
        print "Node 1: ", node1.peer_list
        print "Node 2: ", node2.peer_list
        print "Node 3: ", node3.peer_list
        close_all()