from pygnutella.bootstrap import DagBootstrap
from pygnutella.scheduler import loop as schedule_loop, close_all
import logging
import sys

def main(args):
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
    dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
    DagBootstrap(dag)

    try:
        schedule_loop()
    finally:
        close_all()

if __name__ == "__main__":
    main(sys.argv[1:])