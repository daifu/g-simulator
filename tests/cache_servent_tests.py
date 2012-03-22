from nose.tools import *
from pygnutella.servent import FileInfo
from pygnutella.message import create_message
from pygnutella.messagebody import GnutellaBodyId
from pygnutella.demo.cache_servent import CacheServent

def test_cache():
    test_servent = CacheServent()
    fake_queryhit = create_message(GnutellaBodyId.QUERYHIT)    
    test_servent.save_queryhit(fake_queryhit)
    cache_result = test_servent.search_queryhit("criteria")
    fake_queryhit2 = create_message(GnutellaBodyId.QUERYHIT)
    test_servent.save_queryhit(fake_queryhit2)