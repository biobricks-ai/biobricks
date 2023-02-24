import pytest
import os
import pathlib
import tempfile

import biobricks as bb

@pytest.fixture
def CONFIG():
    oldbb = os.getenv('BBLIB')
    tdir  = tempfile.TemporaryDirectory()
    os.environ['BBLIB'] = tdir.name
    yield pathlib.Path(tdir.name)
    if oldbb: os.environ['BBLIB'] = oldbb
    tdir.cleanup()

# def test_initialize(BBLIB,TOKEN):
#     errmsg = "must use token from https://biobricks.ai/token"
#     with pytest.raises(Exception,match=errmsg) as e:
#         bb.initialize()

#     res = bb.initialize(TOKEN)
#     assert(res == BBLIB)
#     assert(bb.token() == TOKEN)

# def test_bblib(EMPTY_BBLIB):
#     errmsg = "'BBLIB' env not available.*"
#     with pytest.raises(Exception,match=errmsg):
#         bb.bblib()

# def test_load(local_bblib):
#     brick="lkjasdfkjasdklfj"
#     with pytest.raises(Exception,match=".*not available.*"):
#         bb.pull(brick)

#     brick = "hello-brick"
#     org = "biobricks-ai"
#     bb.pull(brick,org)
#     assert bb.bblib(f'{org}/{brick}/data/mtcars.parquet').exists()

#     tbls = bb.load(brick,org)
#     assert tbls.mtcars.shape == (32,11)

#     with pytest.raises(Exception,match="no path.*"):
#         bb.load("a-brick-that-doesn't-exist")
    
#     with pytest.raises(Exception,match=".* not available"):
#         check_url_available("http://the-internet.herokuapp.com/status_codes/301")