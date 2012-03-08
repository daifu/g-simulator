from pygnutella.scheduler import loop as schedule_loop, close_all
from multiprocessing import Process
from time import sleep
import logging

def __create_node(servent_cls, bootstrap_address):
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
    servent_cls(bootstrap_address = bootstrap_address)
    try:
        schedule_loop()
    finally:
        close_all()    

def create_network(preferred_cls, bootstrap_address):
    children = []
    for cls in preferred_cls:        
        p = Process(target = __create_node, args=(cls, bootstrap_address))
        children.append(p)
        p.start()
        # sleep 2 seconds before start another node
        sleep(2)
        
    try:
        for p in children:
            p.join()
    finally:
        for p in children:
            try:
                p.terminate()
                p.join()
            except:
                pass