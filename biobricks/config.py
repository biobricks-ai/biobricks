import os, warnings, json, urllib
from subprocess import run, DEVNULL, STDOUT
from pathlib import Path
import shutil

def biobricks_config_path():
    return Path.home().joinpath(".biobricks")

def read_config():
    path = biobricks_config_path()
    if not path.exists(): return {}
    return json.loads(path.read_text())

def write_config(config):
    path = biobricks_config_path()
    bblib = Path(os.path.expanduser(config['BBLIB']))
    config['BBLIB'] = str(bblib.resolve())
    path.write_text(json.dumps(config))

def init_bblib() -> None:
    if not shutil.which('git'): 
        raise Exception('Program "git" not installed. Please install "git"')
    
    bbpath = Path(read_config()['BBLIB'])
    os.makedirs(bbpath, exist_ok=True)
    os.makedirs(bbpath / "cache", exist_ok=True)
    run("git init", cwd=bbpath, stdout=DEVNULL, stderr=STDOUT, shell=True)
    return bblib()

def check_has_bblib():
    if not 'BBLIB' in read_config(): return False
    if not Path(read_config()["BBLIB"]).exists(): return False
    if not Path(read_config()["BBLIB"]).is_dir(): return False
    if not Path(read_config()["BBLIB"]).joinpath("cache").exists(): return False
    if not Path(read_config()["BBLIB"]).joinpath(".git").exists(): return False
    return True

def bblib(path=""):
    if check_has_bblib(): return Path(read_config()["BBLIB"]) / path
    raise Exception("no BBLIB path. run `biobricks configure` to set your BBLIB path")

def token_url():
    return "https://biobricks.ai/token"

def token():
    if read_config().keys() >= {"TOKEN"}: return read_config()["TOKEN"]
    raise Exception("no token. run `biobricks configure` to set your token")
    
