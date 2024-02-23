import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from biobricks import Brick, cli
from biobricks.config import write_config, init_bblib
import tempfile

def configure(bblib, token, overwrite, interactive):
    
    if not interactive:
        config = { "BBLIB": f"{bblib}", "TOKEN": token }
        write_config(config)
        init_bblib()
        return

class TestBrickResolve(unittest.TestCase):
    
    tempdir = tempfile.TemporaryDirectory()
    
    def setUp(self):
        bblib = Path(f"{TestBrickResolve.tempdir.name}/biobricks")
        bblib.mkdir(exist_ok=True,parents=True)
        configure(f"{bblib}", "VQF6Q2U-NKktZ31ioVYa9w", None, None)

    def tearDown(self) -> None:
        return super().tearDown()

    # test basic install of the hello-brick
    @patch('biobricks.bblib')
    def test_install_hello_brick():
        from biobricks.brick import Brick
        brick = Brick.Resolve("hello-brick")
        brick.install()
        assert brick.path().exists()
        assert (brick.path() / "hello.txt").exists()
        assert (brick.path() / "hello.txt").read_text() == "hello world\n"

if __name__ == '__main__':
    unittest.main()