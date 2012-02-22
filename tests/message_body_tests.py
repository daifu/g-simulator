from nose.tools import *
from pygnutella.messagebody import *
from pygnutella.message import Message

def test_PingBody():
    message = Message('')
    ping = PingBody(message)
    assert_equal(ping.message, message)
    assert_equal(ping.get_length(), 0)
    assert_equal(ping.serialize(), b'')
    
def test_PongBody():
    message = Message('')
    ip = '' 
    port = 5000 
    num_of_files = 0 # TODO: get the real number
    num_of_kb = 0 #  TODO: get the real number
    pong = PongBody(message, ip, port, num_of_files, num_of_kb)
    assert_equal(pong.message, message)
    assert_equal(pong.ip, '')
    assert_equal(pong.port, 5000)
    assert_equal(pong.num_of_files, 0)
    assert_equal(pong.num_of_kb, 0)

def test_QueryBody():
    message = Message('')
    min_speed = 100 # default is 100 kB/sec
    search_criteria = '' # TODO: get the real string
    query = QueryBody(message, min_speed, search_criteria)
    assert_equal(query.min_speed, 100)
    assert_equal(query.search_criteria, search_criteria)

def test_QueryHitBody():
    message = Message('')
    ip = ''
    port = 5000
    speed = 100 # default is 100 kB/sec
    result_set = [] # TODO: create real resut set
    servent_id = ''
    num_of_hits = 0 # TODO: create number of hits
    query_hit = QueryHitBody(message, ip, port, speed, 
                        result_set, servent_id, num_of_hits)
    assert_equal(query_hit.message, message)
    assert_equal(query_hit.ip, '')
    assert_equal(query_hit.port, 5000)
    assert_equal(query_hit.speed, 100)
    assert_equal(query_hit.result_set, [])
    assert_equal(query_hit.servent_id, '')

def test_PushBody():
    message = Message('')
    ip = ''
    port = 5000
    file_index = '' # TODO: a index that find the file from the servent
    push = PushBody(message, ip, port, file_index)
    assert_equal(push.message, message)
    assert_equal(push.ip, '')
    assert_equal(push.port, 5000)
    assert_equal(push.file_index, '')
    
