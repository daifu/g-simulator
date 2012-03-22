from nose.tools import *
from pygnutella.servent import FileInfo
from pygnutella.message import create_message
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.demo.cache_servent import CacheServent
from pygnutella.utils import dotted_quad_to_num

def test_cache():
    test_servent = CacheServent()

    ip = dotted_quad_to_num('127.0.0.1')
    port = 59850
    speed = 100 
    result_set = [{
            'file_index': 3435,
            'file_size': 100,
            'file_name': 'A'
        },
        {
            'file_index': 3535,
            'file_size': 200,
            'file_name': 'B'
        }]
    servent_id = 'thisisservent_id'
    
    fake_queryhit = create_message(GnutellaBodyId.QUERYHIT,
                                   ip = ip,
                                   port = port,
                                   result_set = result_set,
                                   servent_id = servent_id,
                                   speed = 1)

    test_servent.save_queryhit(fake_queryhit)
    cache_result = test_servent.search_queryhit("A")
    # test the result
    assert_equal(len(cache_result), 1)
    assert_equal(cache_result[0][3][0]['file_index'], 3435)
    
    # test the merge
    result_set2 = [{
            'file_index': 3435,
            'file_size': 100,
            'file_name': 'A'
        },
        {
            'file_index': 35345,
            'file_size': 200,
            'file_name': 'C'
        }]    
    fake_queryhit2 = create_message(GnutellaBodyId.QUERYHIT,
                                   ip = ip,
                                   port = port,
                                   result_set = result_set2,
                                   servent_id = servent_id,
                                   speed = 1)
    
    test_servent.save_queryhit(fake_queryhit2)
    # check if it actually merge
    assert_equal(len(test_servent.queryhit_cache), 1)
    
    cache_result = test_servent.search_queryhit("C")
    # test the result
    assert_equal(len(cache_result), 1)
    assert_equal(cache_result[0][3][0]['file_index'], 35345)
    # complex test, use two servent
    servent_id2 = 'thisisserventid1'
    fake_queryhit3 = create_message(GnutellaBodyId.QUERYHIT,
                                   ip = ip,
                                   port = port,
                                   result_set = result_set,
                                   servent_id = servent_id2,
                                   speed = 1)
    test_servent.save_queryhit(fake_queryhit3)
    # test if it does not merge
    assert_equal(len(test_servent.queryhit_cache), 2)
    # test the result
    cache_result = test_servent.search_queryhit("A")
    assert_equal(len(cache_result), 2)
