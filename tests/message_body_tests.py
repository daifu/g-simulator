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
    ip = '127.0.0.1' 
    port = 5000 
    num_of_files = 0 # TODO: get the real number
    num_of_kb = 0 #  TODO: get the real number
    pong = PongBody(message, ip, port, num_of_files, num_of_kb)
    assert_equal(pong.message, message)
    assert_equal(pong.ip, '127.0.0.1')
    assert_equal(pong.port, 5000)
    assert_equal(pong.num_of_files, 0)
    assert_equal(pong.num_of_kb, 0)

    #test the serialize and deserialize
    body = pong.serialize()
    de_body = pong.deserialize()

    body_expected_str =\
    "127.0.0.1\x00\x00\x13\x88\x00\x00\x00\x00\x00\x00\x00\x00"
    de_body_exp_tuple = ('127.0.0.1', 5000, 0, 0)
    size_exp = 21

    assert_equal(pong.body, body_expected_str)
    assert_equal(de_body, de_body_exp_tuple)
    assert_equal(pong.get_length(), size_exp)

def test_QueryBody():
    message = Message('')
    min_speed = 100 # default is 100 kB/sec
    search_criteria = 'helloworld' # TODO: get the real string
    query = QueryBody(message, min_speed, search_criteria)
    assert_equal(query.min_speed, 100)
    assert_equal(query.search_criteria, search_criteria)

    #test the serialize and deserialize
    body = query.serialize()
    de_body = query.deserialize()

    body_expected_str = "\x00\x00\x00dhelloworld"
    de_body_exp_tuple = (100, "helloworld")
    size_exp = 14

    assert_equal(query.body, body_expected_str)
    assert_equal(de_body, de_body_exp_tuple)
    assert_equal(query.get_length(), size_exp)

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
    ip = '127.0.0.1'
    port = 5000
    file_index = 'indexhere'
    push = PushBody(message, ip, port, file_index)
    assert_equal(push.message, message)
    assert_equal(push.ip, '127.0.0.1')
    assert_equal(push.port, 5000)
    assert_equal(push.file_index, 'indexhere')

    #test the serialize and deserialize
    body = push.serialize()
    de_body = push.deserialize()

    body_expected_str = "127.0.0.1\x00\x00\x13\x88indexhere"
    de_body_exp_tuple = ('127.0.0.1', 5000, "indexhere")
    size_exp = 22

    assert_equal(push.body, body_expected_str)
    assert_equal(de_body, de_body_exp_tuple)
    assert_equal(push.get_length(), size_exp)
