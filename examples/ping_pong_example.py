from pygnutella.servent import BasicServent, FileInfo
from pygnutella.message import create_message
from pygnutella.messagebody import GnutellaBodyId
import asyncore
import logging

class SendServent(BasicServent):
    receive_message = []
    sent_message = []
    
    def on_connect(self, connection_handler):
        ping_message = create_message(GnutellaBodyId.PING)
        self.sent_message.append(ping_message)
        self.log("sending %s", ping_message)
        self.log("ping size %s", len(ping_message.serialize()))
        connection_handler.write(ping_message.serialize())
        return
    
    def on_receive(self, connection_handler, message):
        self.log("received %s", message)
        self.receive_message.append(message)
        BasicServent.on_receive(self, connection_handler, message)


class ReceiveServent(BasicServent):
    receive_message = []
    def on_receive(self, connection_handler, message):
        self.receive_message.append(message)
        BasicServent.on_receive(self, connection_handler, message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s') 
    receive_servent = ReceiveServent()
    send_servent = SendServent()
    
    # manually set file
    receive_servent.set_files([FileInfo(1,"first file", 600),  FileInfo(2,"second file", 2500) , FileInfo(3, "third file", 5000)])    
    receive_servent.reactor.gnutella_connect(send_servent.reactor.address)
    
    try:
        asyncore.loop(use_poll = True)
    finally:
        asyncore.close_all()