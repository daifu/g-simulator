from pygnutella.bootstrap import DagBootstrap, SimpleBootstrap, RandomBootstrap
from pygnutella.scheduler import loop as schedule_loop, close_all
import logging
import sys


randombootstrap_usage = "example: for p = 0.7, please python run_bootstrap.py RandomBootstrap 0.7"
dagbootstrap_usage = "an adjacent list is specified as follow\n\
+ a semi-colon denote separation list\n\
+ a colon than sign denote mapping\n\
+ a coma denote separation of node inside a list, but not last node\n\
+ space is not important\n\
+ order is not important\n\
+ repetition will result in override and last copy is the list\n\
example: python run_bootstrap.py DagBootstrap 3 : 1, 2; 1:0; 2:1,0; 3: 0 is\n\
adjacency list {1: [0], 2: [1,0], 3: [0]}"

bootstrap_table = {"SimpleBootstrap": (SimpleBootstrap, ""),
                   "RandomBootstrap": (RandomBootstrap, randombootstrap_usage),
                   "DagBootstrap": (DagBootstrap, dagbootstrap_usage)}

def main(argv, argc):
    print "Please use Ctrl+C to terminate"
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
    if argc == 0:
        print "Running with default behavior."
        print "To see other options, please run with python run_bootstrap.py help"        
        dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
        print "The default is DagBootstrap with %s" % dag
        DagBootstrap(dag)
        
        try:
            schedule_loop()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            close_all()
        return
    
    if argv[0] == 'help':
        if argc == 1:
            print "You could run the following Bootstrap: "
            for bt in bootstrap_table.keys():
                print "* ", bt
            print "You can find out how to run any of above Bootstrap by typing: "
            print "python run_bootstrap.py help <bootstrap name>"
        elif argv[1] == 'SimpleBootstrap':
            # TODO: explain SimpleBootstrap
            pass        
        elif argv[1] == 'RandomBootstrap':
            # TODO: explain RandomBootstrap
            pass        
        elif argv[1] == 'DagBootstrap':
            # TODO: explain DagBootstrap
            pass
        return
    
    if argv[0] == 'SimpleBootstrap':
        # TODO
        return
    
    if argv[0] == 'RandomBootstrap':
        # TODO
        return
    
    if argv[0] == 'DagBootstrap':
        # TODO
        return

if __name__ == "__main__":
    main(sys.argv[1:], len(sys.argv)-1)