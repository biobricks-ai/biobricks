import pytest
import os
import pathlib
import tempfile

import biobricks as bb
from ..pull import check_url_available
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
    return "8dxRZmQFbQ1QuIcg6u9fdw"

def test_initialize(BBLIB,TOKEN):
    errmsg = "must use token from https://members.biobricks.ai/token"
    with pytest.raises(Exception,match=errmsg) as e:
        bb.initialize()

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
    errmsg = "'BBLIB' env not available.*"
    with pytest.raises(Exception,match=errmsg):
        bb.bblib()

@pytest.fixture
def local_bblib(TOKEN):
    oldbb = os.getenv('BBLIB')
    tdir  = tempfile.TemporaryDirectory()
    os.environ['BBLIB'] = tdir.name
    bb.initialize(TOKEN)
    yield pathlib.Path(tdir.name)
    if oldbb: os.environ['BBLIB'] = oldbb
    tdir.cleanup()

def test_load(local_bblib):
    brick="lkjasdfkjasdklfj"
    with pytest.raises(Exception,match=".*not available.*"):
        bb.pull(brick)

    brick = "hello-brick"
    org = "biobricks-ai"
    bb.pull(brick,org)
    assert bb.bblib(f'{org}/{brick}/data/mtcars.parquet').exists()

    tbls = bb.load(brick,org)
    assert tbls.mtcars.shape == (32,11)

    with pytest.raises(Exception,match="no path.*"):
        bb.load("a-brick-that-doesn't-exist")
    
    with pytest.raises(Exception,match=".* not available"):
        check_url_available("http://the-internet.herokuapp.com/status_codes/301")