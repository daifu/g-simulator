from nose.tools import *
from pygnutella.servent import BasicServent, FileInfo
from pygnutella.message import create_message
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.scheduler import loop as scheduler_loop, close_all
from copy import deepcopy

class SendServent(BasicServent):
    def __init__(self):
        self.receive_message = []
        self.sent_message = []
        BasicServent.__init__(self)
    def on_connect(self, connection_handler):
        ping_message = create_message(GnutellaBodyId.PING)
        self.sent_message.append(ping_message)
        self.send_message(ping_message, connection_handler)
        return

    def on_receive(self, connection_handler, message):
        self.receive_message.append(message)
        BasicServent.on_receive(self, connection_handler, message)

class ReceiveServent(BasicServent):
    def __init__(self):
        BasicServent.__init__(self)
        self.receive_message = []

    def on_receive(self, connection_handler, message):
        self.receive_message.append(deepcopy(message))
        BasicServent.on_receive(self, connection_handler, message)

class TestHandler():
    def write(self, data):
        return

def test_on_receive():
    # test all logic path in on_receive(
    basic_servent = BasicServent()
    test_handler = TestHandler()
    ping_message = create_message(GnutellaBodyId.PING)
    basic_servent.on_receive(test_handler, ping_message)
    # second one test on forward table
    basic_servent.on_receive(test_handler, ping_message)
    pong_message = create_message(GnutellaBodyId.PONG, ip = basic_servent.reactor.ip, 
                                  port = basic_servent.reactor.port, num_of_files = 0, 
                                  num_of_kb = 0)
    basic_servent.on_receive(test_handler, pong_message)
    pong_message2 = create_message(GnutellaBodyId.PONG, message_id = ping_message.message_id,
                                   ip = basic_servent.reactor.ip, port = basic_servent.reactor.port, 
                                   num_of_files = 0, num_of_kb = 0)
    basic_servent.on_receive(test_handler, pong_message2)
    query_message = create_message(GnutellaBodyId.QUERY, min_speed = 2, search_criteria = 'hello world')
    basic_servent.on_receive(test_handler, query_message)
    #queryhit_message = create_message(GnutellaBodyId.QUERYHIT)
    #TODO:
    close_all()

def test_servent():
    receive_servent = ReceiveServent()
    send_servent = SendServent()
    assert_equal(receive_servent.files, [])
    assert_equal(send_servent.files, [])

    # manually set file
    receive_servent.set_files([FileInfo(1,"first file", 600),  FileInfo(2,"second file", 2500) , FileInfo(3, "third file", 5000)])
    assert_equal(receive_servent.check_file(1), True)
    assert_equal(receive_servent.check_file(200), False)

    receive_servent.reactor.gnutella_connect(send_servent.reactor.address)
    try:
        scheduler_loop(timeout=1,count=10)
    finally:
        assert_equal(len(send_servent.sent_message), 1)
        assert_equal(len(receive_servent.receive_message), 1)
        assert_equal(receive_servent.receive_message[0].message_id, send_servent.sent_message[0].message_id)
        assert_equal(receive_servent.receive_message[0].ttl, send_servent.sent_message[0].ttl)
        assert_equal(receive_servent.receive_message[0].hops, send_servent.sent_message[0].hops)
        assert_equal(receive_servent.receive_message[0].payload_length, send_servent.sent_message[0].payload_length)
        assert_equal(receive_servent.receive_message[0].payload_descriptor, send_servent.sent_message[0].payload_descriptor)
        assert_equal(receive_servent.receive_message[0].serialize(), send_servent.sent_message[0].serialize())
        assert_equal(len(send_servent.receive_message), 1)
        assert_equal(send_servent.receive_message[0].body.num_of_files, 3)
        assert_equal(send_servent.receive_message[0].body.num_of_kb, 8)
        close_all()
