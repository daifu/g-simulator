from ..servent import BasicServent

class LogServent(BasicServent):    
    def __init__(self, port = 0, files = [], bootstrap_address = None):
        BasicServent.__init__(self, port, files, bootstrap_address)
        self.num_requested_conn = 0
        self.num_accepted_conn = 0
        self.num_rx_byte = 0
        self.num_tx_byte = 0
    
    def on_accept(self):
        self.num_requested_conn += 1
        return BasicServent.on_accept(self)
    
    def on_connect(self, connection_handler):
        self.num_accepted_conn += 1
        BasicServent.on_connect(self, connection_handler)
        
    def on_receive(self, connection_handler, message):
        self.num_rx_byte += len(message.serialize())
        BasicServent.on_receive(self, connection_handler, message)
                
    def send_message(self, message, handler):
        self.num_tx_byte += len(message.serialize())
        BasicServent.send_message(self, message, handler)        
        
    def forward(self, message):
        ret = BasicServent.forward(self, message)
        if ret:
            self.num_tx_byte += len(message.serialize())
        return ret
    
    def flood(self, connection_handler, message):
        ret = BasicServent.flood(self, connection_handler, message) 
        self.num_tx_byte += len(message.serialize())*ret
        return ret        
        
