from context import IContext
from message import Message

class HandShakeState:
    SENDING_WELCOME = 0
    RECEIVING_RESPONSE = 1     
    RECEIVING_WELCOME = 2
    SENDING_RESPONSE = 3       
    COMPLETED_AND_SUCCEEDED = 4
        
class HandShake:
    WELCOME_MESSAGE = 'GNUTELLA CONNECT/0.4\n\n'
    RESPONSE_MESSAGE = 'GNUTELLA OK\n\n'

class HandShakeCompleteContext(IContext):
    def __init__(self, handler):
        IContext.__init__(self, handler)
        self.handler.reactor.connector(handler)
        self.handler.reactor.add_channel(handler)
        self.on_read()       
        return
    
    def on_read(self):
        self.logger.debug("on_read()")
        try:
            msg = Message()
            msg_length = msg.deserialize(self.handler.received_data)
            if msg_length:
                self.handler.reactor.receiver(self.handler, msg)
                self.handler.received_data = self.handler.received_data[msg_length:]
            else:
                self.logger.debug("on_read() -> incomplete message")
        except ValueError:
            # The message stream is messed up
            self.logger.debug("on_read() -> mesage stream is messed up")
            self.handler.handle_close()
        return self

class HandShakeInContext(IContext):
    def __init__(self, handler):
        IContext.__init__(self, handler)
        self.on_read()
        return
    
    def on_read(self):
        self.logger.debug("on_read()")
        size = len(HandShake.WELCOME_MESSAGE)
        if len(self.handler.received_data) >= size:
            if HandShake.WELCOME_MESSAGE == self.handler.received_data[:size]:
                self.logger.debug("on_read() got Welcome Message")
                if self.handler.reactor.acceptor():
                    self.handler.write(HandShake.RESPONSE_MESSAGE)
                    self.handler.received_data = self.handler.received_data[size:]
                    self.logger.debug("transit to HandShakeCompleteContext")
                    return HandShakeCompleteContext(self.handler)
                else:
                    self.handler.handle_close()
        return self

class HandShakeOutContext(IContext):
    def __init__(self, handler):
        IContext.__init__(self, handler)
        self.handler.write(HandShake.WELCOME_MESSAGE)
        self.logger.debug("sending Welcome Message")
        self.on_read()
        return
    
    def on_read(self):
        self.logger.debug("on_read()")
        size = len(HandShake.RESPONSE_MESSAGE)
        if len(self.handler.received_data) >= size:
            if HandShake.RESPONSE_MESSAGE == self.handler.received_data[:size]:
                self.logger.debug("on_read() got Response Message")
                self.handler.received_data = self.handler.received_data[size:]
                self.logger.debug("transit to HandShakeCompleteContext")
                return HandShakeCompleteContext(self.handler)            
        return self