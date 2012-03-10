class IContext:
    """
    IContext is a way to implement state in asynchronous network program
    
    Context is a state. In __init__ (i.e. initialization),
    a writer i.e. a function to write output, and a buffer that
    is leftover from previous state optionally. Also, return the state itself
    
    on_read is called when an input (i.e data) comes in. on_read return a state.
    The current state (i.e. self variable) or new state. 
    """
    def __init__(self, handler, data=None):
        self.handler = handler
        self.handler.set_context(self)
        return
    
    def on_read(self):
        raise NotImplementedError
    
    def on_close(self):
        raise NotImplementedError
        
class DeadContext(IContext):
    """
    Do nothing Context
    """
    def on_read(self):
        return
    
    def on_close(self):
        return