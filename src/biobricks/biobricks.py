import os
from os.path import exists
import pkg_resources
import json
# import numpy as np
# import pandas as pd
# import pyarrow as pa
import pyarrow.parquet as pq
import urllib.request
from typing import Any, Dict

BASE_DIR = os.path.expanduser('~')+'/biobricks'
CONFIG_FILE = BASE_DIR+'/config.json'
config = None
library = None
bricks = []

def version():
    version = pkg_resources.get_distribution("biobricks").version
    print(f"BioBricks Version {version}")

def initialize() -> None:
    global config, library, bricks
    os.makedirs(BASE_DIR, exist_ok=True)
    if exists(CONFIG_FILE):
        with open(CONFIG_FILE) as file:
            config = json.load(file)
        library = config["library"]
        bricks = config["bricks"]
        print(f"BioBricks library already intialized to {library}.")
    else:
        bblib = os.getenv("bblib")
        if bblib:
            library = bblib
        else:
            library = BASE_DIR+'/library'
        config = { 'library': library, 'bricks': [], }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        os.makedirs(library, exist_ok=True)
        os.makedirs(library+"/cache", exist_ok=True)
        if not exists(library+"/.git"):
            os.system(f"cd {library}; git init")
        print(f"Initialized BioBricks library to {library}.")

def pull(brick):
    global config, library, bricks
    print(f"Pulling brick {brick} from GitHub and S3 AWS.")
    repo = "biobricks-ai/"+brick
    url = "https://github.com/"+repo
    if urllib.request.urlopen(url).getcode()!=200:
        print(f"Brick {brick} is not available in BioBricks.")
        return False
    repodir = library+"/"+repo
    os.system(f"cd {library}; git submodule add {url} {repo}")
    os.system(f"cd {repodir}; dvc cache dir ../../cache")
    os.system(f"cd {repodir}; dvc config cache.shared group")
    os.system(f"cd {repodir}; dvc config cache.type symlink")
    for i in range(5):
        print(f"Attemp {i} to pull")
        code = os.system(f"cd {repodir}; dvc pull brick")
        print(f"Pulling output code: {code}")
        if code==0:
            break
        elif i==4:
            print(f"Pulling error.")
            return False
    os.system(f"cd {library}; git commit -m \"added {repo}\"")
    bricks += [brick]
    config['bricks'] = bricks
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    return True

def load(brick):
    global library, config, bricks
    if library is None:
        initialize()
    if not brick in bricks:
        if not pull(brick):
            print(f"Can't load brick {brick}.")
            return None
    print(f"Loading brick {brick} from local library.")
    brickpq = library+"/biobricks-ai/"+brick+"/brick"
    return pq.read_table(brickpq)

# def remove(brick):
#     global library, config, bricks

def listbricks():
    print(bricks)
