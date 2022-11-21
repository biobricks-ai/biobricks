import pytest
import os
import pathlib
import tempfile

import biobricks as bb
from unittest.mock import Mock

@pytest.fixture
def BBLIB():
    oldbb = os.getenv('BBLIB')
    tdir  = tempfile.TemporaryDirectory()
    os.environ['BBLIB'] = tdir.name
    yield pathlib.Path(tdir.name)
    if oldbb: os.environ['BBLIB'] = oldbb
    tdir.cleanup()

@pytest.fixture
def TOKEN():
    return "alksdjfklasdjflk"

def test_initialize(BBLIB,TOKEN):
    errmsg = f"must initialize with token at https://members.biobricks.ai/token"
    with pytest.raises(Exception,match=errmsg) as e:
        bb.initialize()

    res = bb.initialize(TOKEN)
    assert(res == BBLIB)

    warnmsg = f"Not initializing, BBLIB is already '{BBLIB}'"
    with pytest.warns(UserWarning, match=warnmsg):
        res = bb.initialize(TOKEN)
        assert(res == BBLIB)
    
    assert(bb.token() == TOKEN)

@pytest.fixture
def EMPTY_BBLIB():
    oldbb = os.getenv('BBLIB')
    del os.environ['BBLIB']
    yield 
    if oldbb: os.environ['BBLIB'] = oldbb

def test_bblib(EMPTY_BBLIB):
    warn_msg = "'BBLIB' ENVIRONMENT NOT SET\nUSING DEFAULT ~/biobricks"
    with pytest.warns(UserWarning,match=warn_msg):
        res = bb.bblib()
        assert(res == pathlib.Path.home() / 'biobricks')

@pytest.fixture
def local_bblib(TOKEN):
    oldbb = os.getenv('BBLIB')
    tdir  = tempfile.TemporaryDirectory()
    os.environ['BBLIB'] = tdir.name
    bb.initialize(TOKEN)
    yield pathlib.Path(tdir.name)
    if oldbb: os.environ['BBLIB'] = oldbb
    tdir.cleanup()

def test_config_add(local_bblib):
    init_config = bb.config() | {'a':2}
    bb.config_add({'a':2})
    assert(bb.config() == init_config)
