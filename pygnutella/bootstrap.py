from servent import Servent
from multiprocessing import Process, Pipe
from scheduler import loop as scheduler_loop

class Command:
    """
    This is a list of command send from "bootstrap" process
    to other process for setup.
    """
    # connect command have following ip and port
    # CONNECT 127.0.1.1 8934
    CONNECT = "CONNECT"
    START = "START"
    ON = "ON"
    INFO = "INFO"

class Event:
    """
    This is a list of event
    
    All event log begin with ON <event> <other parameters>
    """
    # example
    # ON LISTENNING <id-hex-string> 127.0.1.1 8945
    LISTENING = "LISTENNING"
    RECEIVED = "RECEIVED"


def construct_command(cmd, **kwargs):
    if cmd == Command.CONNECT:
        return "%s %s %s" % (Command.CONNECT, kwargs['ip'], kwargs['port'])
    elif cmd == Command.START:
        return Command.START
    else:
        raise ValueError

def deconstruct_command(raw_cmd):
    tokens = raw_cmd.split()
    cmd = tokens[0]
    if cmd == Command.CONNECT:
        return {'command': cmd, 'ip': tokens[1], 'port': tokens[2]}
    return None

def create_gnutella_node(servent_class, pipe, files):
    servent = servent_class()
    # TODO: fixed this
    pipe.send('ON LISTENNING %s %s %s' % ('myhex_id', '127.0.1.1', '3945'))
    # TODO: receiving peer list
    while True:
        cmd = pipe.recv()        
        if cmd == 'START':
            break
        else:
            # TODO process command
            pass        
    scheduler_loop()
    pipe.close()

_nodes = []

def create_gnutella_network(num_nodes = 10, adjacent_list, preferred_list = []):
    for _ in xrange(num_nodes):
        parent_conn, child_conn = Pipe()
        p = Process(target = create_gnutella_node, args=(Servent, child_conn,)).start()
        _nodes.append((parent_conn, p))