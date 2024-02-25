import unittest
from unittest.mock import patch
from pathlib import Path
from biobricks import Brick
from biobricks.config import write_config, init_bblib
import tempfile
import pandas as pd
import sqlite3
import os

class BrickTests(unittest.TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        bblib = Path(f"{self.tempdir.name}/biobricks")
        bblib.mkdir(exist_ok=True,parents=True)
        token = os.environ.get("BIOBRICKS_TEST_TOKEN")
        config = { "BBLIB": f"{bblib}", "TOKEN": token }
        write_config(config)
        init_bblib()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_install_hello_brick(self):
        brick = Brick.Resolve("hello-brick")
        brick.install()

        paths = [
            "brick/iris.sqlite",
            "brick/mtcars.parquet",
            "brick/rtbls/iris.parquet",
            "brick/rtbls/mtcars.parquet"
        ]
        
        # Check if all paths exist
        for path in paths:
            self.assertTrue((brick.path() / path).exists())
        
        # Testing data frames
        df_mtcars = pd.read_parquet(brick.path() / "brick/mtcars.parquet")
        self.assertEqual(df_mtcars.shape, (32, 11))

        df_iris = pd.read_parquet(brick.path() / "brick/rtbls/iris.parquet")
        self.assertEqual(df_iris.shape, (150, 5))

        # Testing SQLite data
        with sqlite3.connect(brick.path() / "brick/iris.sqlite") as con:
            df_sql = pd.read_sql_query("SELECT * FROM iris", con)
            self.assertEqual(df_sql.shape, (150, 5))
    
    def test_uninstall_hello_brick(self):
        brick = Brick.Resolve("hello-brick")
        brick.install()
        self.assertTrue(brick.path().exists())
        brick.uninstall()
        self.assertFalse(brick.path().exists())
    
    def test_assets_hello_brick(self):
        brick = Brick.Resolve("hello-brick")
        brick.install()
        assets = brick.assets()
        self.assertTrue(hasattr(assets, "iris_sqlite"))
        self.assertTrue(hasattr(assets, "mtcars_parquet"))
        self.assertTrue(hasattr(assets, "rtbls_iris_parquet"))
        self.assertTrue(hasattr(assets, "rtbls_mtcars_parquet"))
    
    @patch('biobricks.checks.can_symlink', return_value=False)
    def test_install_without_symlink(self, mocked_can_symlink):
        brick = Brick.Resolve("hello-brick")
        brick.install()

        paths = [
            "brick/iris.sqlite",
            "brick/mtcars.parquet",
            "brick/rtbls/iris.parquet",
            "brick/rtbls/mtcars.parquet"
        ]

        for path in paths:
            full_path = brick.path() / path
            self.assertTrue(full_path.exists())
            self.assertFalse(full_path.is_symlink(), f"{path} should not be a symlink")

if __name__ == '__main__':
    unittest.main()