from pygnutella.bootstrap import DagBootstrap, SimpleBootstrap, RandomBootstrap
from pygnutella.scheduler import loop as schedule_loop, close_all
import logging
import sys

additional_note = "Note: if you want to run our network with this bootstrap, \
please open another terminal in the same directory and run\n\
python run_servent.py <bootstrap_ip> <bootstrap_port> <num of node>"

bootstraps = [SimpleBootstrap, RandomBootstrap, DagBootstrap]
bt_name = [bt.__name__ for bt in bootstraps]

def main(argv, argc):    
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
    if argc == 0:
        print "Running with default behavior."
        print "To see other options, please run with python run_bootstrap.py help"        
        dag = {0: [], 1:[0], 2:[0], 3:[1,2]}
        print "The default is DagBootstrap with %s" % dag
        print "Please use Ctrl+C to terminate"
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
            for bt in bt_name:
                print "* ", bt
            print "You can find out how to run any of above Bootstrap by typing: "
            print "python run_bootstrap.py help <bootstrap name>"
        else:
            name = argv[1]
            for bt in bootstraps:
                if bt.__name__ == name:
                    if bt.__doc__:
                        print bt.__doc__
                        print additional_note
                    return
            print "We cannot find a bootstrap with name %s" % name
        return
    elif argv[0] in bt_name:
        name = argv[0]
        for bt in bootstraps:
            if bt.__name__ == name:
                kwargs = bt.parse(argv[1:])
                bt(**kwargs)
                
                try:
                    schedule_loop()
                except (KeyboardInterrupt, SystemExit):
                    pass
                finally:
                    close_all()
                return
    else:
        print "No parameter matches. Please python run_bootstrap.py help for help"

if __name__ == "__main__":
    main(sys.argv[1:], len(sys.argv)-1)
