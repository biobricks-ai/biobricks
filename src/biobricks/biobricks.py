import os
from os.path import exists
import pkg_resources
import json
from typing import Any, Dict

# Location of biobricks library
CONFIG_FILE = '~/biobricks/config.json'

# Current version
def version():
    version = pkg_resources.get_distribution("biobricks").version
    print(f"BioBricks Version {version}")

def load(brick):
    initialize()
    print(f"Loading brick {brick} from {library}.")

def read_config() -> Dict[str, Any]:
    with open(CONFIG_FILE) as f:
        return json.load(f)

def write_config(config: Dict[str, Any]) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def initialize() -> None:
    if exists(CONFIG_FILE):
        config = read_config()
    else:
        bblib = os.getenv("bblib")
        if bblib:
            library = bblib
        else:
            library = '~/biobricks/library'
        config = {
            'library': library,
        }
        write_config(config)
        if not exists(library):
            os.system(f"mkdir -p {library}")
        if not exists(library+"/.git"):
            os.system(f"cd {library}; git init")
        if not exists(library+"/cache"):
            os.system(f"cd {library}; mkdir -p cache")
        print(f"Initialized BioBricks library to {library}.")
    globals().update(config)
