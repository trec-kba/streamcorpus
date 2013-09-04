import os
import uuid
import time
import errno
import pytest
import logging
## utility for tests that configures logging in roughly the same way
## that a program calling bigtree should setup logging
logger = logging.getLogger('streamcorpus')
logger.setLevel( logging.DEBUG )
ch = logging.StreamHandler()
ch.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

## import from inside the local package, i.e. get these things through __init__.py
from . import make_stream_time

def test_make_stream_time_zero():
    st = make_stream_time(epoch_ticks=0)
    assert st.epoch_ticks == 0
    assert st.zulu_timestamp == '1970-01-01T00:00:00.000000Z'

# datetime.datetime(2013, 9, 4, 18, 41, 30, 333363)
# '2013-09-04T18:41:30.333363Z'
# 1378320090.333363

def test_make_stream_time_2013_ticks():
    st = make_stream_time(epoch_ticks=1378320090.333363)
    assert st.epoch_ticks == 1378320090.333363
    assert st.zulu_timestamp == '2013-09-04T18:41:30.333363Z'

def test_make_stream_time_2013_string():
    st = make_stream_time('2013-09-04T18:41:30.333363Z')
    assert int(st.epoch_ticks) == int(1378320090.333363)  # strptime loses microseconds
    assert st.zulu_timestamp == '2013-09-04T18:41:30.333363Z'

def test_make_stream_time_2013_string_noDST():
    st = make_stream_time('2013-01-04T18:41:30.333363Z')
    assert st.epoch_ticks == 1357324890.0  # strptime loses microseconds
    assert st.zulu_timestamp == '2013-01-04T18:41:30.333363Z'

def test_make_stream_time_2013_string_noDST_round_trip():
    st = make_stream_time('2013-01-04T18:41:30.000000Z')
    st2 = make_stream_time(epoch_ticks=st.epoch_ticks)
    assert st.epoch_ticks == 1357324890.0  # strptime loses microseconds
    assert st.zulu_timestamp == '2013-01-04T18:41:30.000000Z'
    assert st.zulu_timestamp == st2.zulu_timestamp

def test_make_stream_time_number_round_trip():
    st = make_stream_time(epoch_ticks=12341234)
    st2 = make_stream_time(st.zulu_timestamp)
    assert st2.epoch_ticks == st.epoch_ticks

def test_make_stream_time_now_round_trip():
    st = make_stream_time()
    st2 = make_stream_time(st.zulu_timestamp)
    assert int(st2.epoch_ticks) == int(st.epoch_ticks)
    st3 = make_stream_time(epoch_ticks=st.epoch_ticks)
    st4 = make_stream_time(st3.zulu_timestamp)
    assert int(st4.epoch_ticks) == int(st.epoch_ticks)

