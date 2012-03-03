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
    def __init__(self, handler, received_data):
        IContext.__init__(self, handler, received_data)
        handler.reactor.connector(handler)
        handler.reactor.add_channel(handler)        
        return
    
    def on_read(self):
        try:
            msg = Message()
            msg_length = msg.deserialize(self.handler.received_data)
            if msg_length:
                self.handler.reactor.receiver(self, msg)
                self.handler.received_data = self.received_data[msg_length:]               
        except ValueError:
            # The message stream is messed up
            self.logger.debug("handle_read() -> mesage stream is messed up")
            self.handler.handle_close()
        return

class HandShakeSendingResponse(IContext):
    def __init__(self, handler):
        IContext.__init__(self, handler)
        return
    
    def on_read(self):
        size = len(HandShake.WELCOME_MESSAGE)
        if len(self.handler.received_data) > size:
            if HandShake.WELCOME_MESSAGE == self.handler.received_data[:size]:
                self.handler.write(HandShake.RESPONSE_MESSAGE)
                self.handler.received_data = self.handler.received_data[size:]
                return HandShakeCompleteContext(self, self.handler)

class HandShakeSendingWelcome(IContext):
    def __init__(self, handler):
        IContext.__init__(self, handler)
        self.handler.write(HandShake.WELCOME_MESSAGE)
        return
    
    def on_read(self):
        size = len(HandShake.RESPONSE_MESSAGE)
        if len(self.handler.received_data) > size:
            if HandShake.RESPONSE_MESSAGE == self.handler.received_data[:size]:
                self.handler.received_data = self.handler.received_data[size:]
                return HandShakeCompleteContext(self, self.handler)        

class HandShakeContext(IContext):