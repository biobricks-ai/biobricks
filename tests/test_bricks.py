import unittest
from unittest.mock import patch
from pathlib import Path
from biobricks import Brick
from biobricks.config import write_config, init_bblib, token
import tempfile
import pandas as pd
import sqlite3
import os

class BrickTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = os.environ.get("BIOBRICKS_TEST_TOKEN",None) or token()
            
        # Create a temporary directory for the whole class
        cls.class_temp_dir = tempfile.TemporaryDirectory()
        cls.temp_biobricks_config_path = Path(cls.class_temp_dir.name) / "biobricks_config_temp.json"

        # Patch the biobricks.config.biobricks_config_path static method
        cls.patcher = patch('biobricks.config.biobricks_config_path', return_value=cls.temp_biobricks_config_path)
        cls.mock_biobricks_config_path = cls.patcher.start()
    
    @classmethod
    def tearDownClass(cls):
        # Stop the patch after all tests in the class
        cls.patcher.stop()
        # Clean up the temporary directory for the class
        cls.class_temp_dir.cleanup()

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        bblib = Path(f"{self.tempdir.name}/biobricks")
        bblib.mkdir(exist_ok=True,parents=True)
        config = { "BBLIB": f"{bblib}", "TOKEN": BrickTests.token }
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

    def test_force_redownload_hello_brick(self):
        brick = Brick.Resolve("hello-brick")
        
        # Initial install
        brick.install()
        initial_mtime = (brick.path() / "brick/iris.sqlite").stat().st_mtime
        
        # Wait a second to ensure the modification time will be different if files are redownloaded
        import time
        time.sleep(1)
        
        # Regular install (should not redownload)
        brick.install()
        regular_mtime = (brick.path() / "brick/iris.sqlite").stat().st_mtime
        
        # Check that the file was not redownloaded
        self.assertEqual(initial_mtime, regular_mtime, "File was redownloaded when it shouldn't have been")
        
        # Force redownload
        brick.install(force_redownload=True)
        force_mtime = (brick.path() / "brick/iris.sqlite").stat().st_mtime
        
        # Check if the file was actually redownloaded (modification time should be different)
        self.assertNotEqual(initial_mtime, force_mtime, "File was not redownloaded when force_redownload was True")
        
        # Check if all expected files still exist after force redownload
        paths = [
            "brick/iris.sqlite",
            "brick/mtcars.parquet",
            "brick/rtbls/iris.parquet",
            "brick/rtbls/mtcars.parquet"
        ]
        for path in paths:
            self.assertTrue((brick.path() / path).exists(), f"{path} should exist after force redownload")

if __name__ == '__main__':
    unittest.main()