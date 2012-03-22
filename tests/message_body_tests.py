from nose.tools import *
from pygnutella.messagebody import PingBody, PongBody, QueryBody, QueryHitBody, PushBody
from pygnutella.message import Message
from pygnutella.utils import dotted_quad_to_num

def test_PingBody():
    message = Message('')
    ping = PingBody(message)
    assert_equal(ping.message, message)
    assert_equal(ping.serialize(), '')

def test_PongBody():
    message = Message('')
    # convert decimal dotted quad string to long integer
    ip = dotted_quad_to_num('127.0.0.1') 
    port = 5000 
    num_of_files = 1 
    num_of_kb = 255 
    pong = PongBody(message, ip, port, num_of_files, num_of_kb)
    assert_equal(pong.message, message)
    assert_equal(pong.ip, ip)
    assert_equal(pong.port, 5000)
    assert_equal(pong.num_of_files, 1)
    assert_equal(pong.num_of_kb, 255)

    #test serialize
    body = pong.serialize()    
    body_expected_str = "\x13\x88\x01\x00\x00\x7f\x00\x00\x00\x01\x00\x00\x00\xff"
    assert_equal(body, body_expected_str)

    # test deserialize
    de_pong = PongBody(message)
    de_pong.deserialize(body_expected_str)
    assert_equal(de_pong.message, message)
    assert_equal(de_pong.ip, ip)
    assert_equal(de_pong.port, 5000)
    assert_equal(de_pong.num_of_files, 1)
    assert_equal(de_pong.num_of_kb, 255)
    
def test_QueryBody():
    message = Message('')
    min_speed = 100 
    search_criteria = 'helloworld' 
    query = QueryBody(message, min_speed, search_criteria)
    assert_equal(query.min_speed, 100)
    assert_equal(query.search_criteria, 'helloworld')

    #test the serialize
    body = query.serialize()    
    body_expected_str = "\x64helloworld\x00"    
    assert_equal(body, body_expected_str)
    
    # test the deserialize
    de_query = QueryBody(message)
    de_query.deserialize(body_expected_str)
    assert_equal(de_query.min_speed, 100)
    assert_equal(de_query.search_criteria, 'helloworld')

    
def test_QueryHitBody():
    message = Message('')
    ip = dotted_quad_to_num('127.0.0.1')
    port = 59850
    speed = 100 
    result_set = [{
            'file_index': 3435,
            'file_size': 100,
            'file_name': 'a_name'
        },
        {
            'file_index': 3535,
            'file_size': 200,
            'file_name': 'b_name'
        }]
    servent_id = 'thisisservent_id'
    num_of_hits = len(result_set)
    query_hit = QueryHitBody(message, ip, port, speed, result_set, servent_id)
    assert_equal(query_hit.message, message)
    assert_equal(query_hit.ip, ip)
    assert_equal(query_hit.port, 59850)
    assert_equal(query_hit.speed, 100)
    assert_equal(query_hit.result_set, result_set)
    assert_equal(query_hit.servent_id, servent_id)

    #test the serialize
    body = query_hit.serialize()
    body_expected_str = "\x02\xe9\xca\x7f\x00\x00\x01\x00\x00\x00\x64\x00\x00\x0d\x6b\x00\x00\x00\x64a_name\x00\x00\x00\x00\x0d\xcf\x00\x00\x00\xc8b_name\x00\x00thisisservent_id"
    assert_equal(body, body_expected_str)
    
    #test the deserialize
    de_queryhit = QueryHitBody(message)
    de_queryhit.deserialize(body_expected_str)
    assert_equal(de_queryhit.ip, ip)
    assert_equal(de_queryhit.port, 59850)
    assert_equal(de_queryhit.speed, 100)
    assert_equal(de_queryhit.result_set, result_set)
    assert_equal(de_queryhit.servent_id, servent_id)

def test_PushBody():
    message = Message('')
    ip = dotted_quad_to_num('127.0.0.1')
    port = 5000
    file_index = 2565
    servent_id = 'thisisservent_id'
    push = PushBody(message, servent_id, ip, port, file_index)
    assert_equal(push.message, message)
    assert_equal(push.ip, ip)
    assert_equal(push.port, 5000)
    assert_equal(push.file_index, 2565)
    assert_equal(push.servent_id, 'thisisservent_id')

    #test the serialize
    body = push.serialize()
    body_expected_str = "thisisservent_id\x00\x00\x0a\x05\x7f\x00\x00\x01\x13\x88"
    assert_equal(body, body_expected_str)

    # test the deserialize
    push_de = PushBody(message)
    push_de.deserialize(body_expected_str)
    assert_equal(push_de.ip, ip)
    assert_equal(push_de.port, 5000)
    assert_equal(push_de.file_index, 2565)
    assert_equal(push_de.servent_id, 'thisisservent_id')    
