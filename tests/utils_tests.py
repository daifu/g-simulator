from nose.tools import *
from pygnutella.utils import *

def test_utils():
    # take straight out of gnutella specification 0.4 page 2
    assert_equal(dotted_quad_to_num('208.17.50.4'), 0xD0113204)
    assert_equal(num_to_dotted_quad(0xD0113204), '208.17.50.4')