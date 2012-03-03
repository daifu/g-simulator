class IContext:
    """
    IContext is a way to implement state in asynchronous network program
    
    Context is a state. In __init__ (i.e. initialization),
    a writer i.e. a function to write output, and a buffer that
    is leftover from previous state optionally. Also, return the state itself
    
    When execute writer, you can assume that all data is write out immediately.
    
    on_read is called when an input (i.e data) comes in. on_read return a state.
    The current state (i.e. self variable) or new state. 
    """
    def __init__(self, writer, buffer=''):
        assert callable(writer)
        self.buffer = buffer
        self.writer = writer
        return
    
    def on_read(self, data):
        raise NotImplementedError
        