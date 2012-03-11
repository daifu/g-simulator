from ..servent import BasicServent

class LogServent(BasicServent):
    def on_accept(self):
        self.log("on_accept()")
        return BasicServent.on_accept(self)
    
    def on_connect(self, connection_handler):
        self.log("on_connect()")
        BasicServent.on_connect(self, connection_handler)
        
    def on_receive(self, connection_handler, message):
        self.log("on_receive() -> %s", message)
        BasicServent.on_receive(self, connection_handler, message)
        
    def on_disconnect(self, connection_handler):
        self.log("on_disconnect()")
        BasicServent.on_disconnect(self, connection_handler)
        
    def on_download(self, event_id, connection_handler):
        self.log("on_download()")
        BasicServent.on_download(self, event_id, connection_handler)
        
    def on_bootstrap(self, peer_address):
        self.log("on_bootstrap() -> %s %s" % peer_address)
        BasicServent.on_bootstrap(self, peer_address)
        
    def forward(self, message):
        self.log("attempt to forward() -> %s", message)
        ret = BasicServent.forward(self, message)
        if ret:
            self.log("forwarded")
        else:
            self.log("didn't forward")
        return ret
    
    def flood(self, connection_handler, message):
        self.log("flood() -> %s", message)
        ret = BasicServent.flood(self, connection_handler, message)
        self.log("number of flooded connection = %d", ret)
        return ret