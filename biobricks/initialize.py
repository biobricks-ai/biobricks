import os

from .token import update_token
from .bblib import bblib

def initialize(token=None) -> None:
    errmsg = "must use token from https://members.biobricks.ai/token"
    if token is None: raise Exception(errmsg)
      
    os.makedirs(bblib(), exist_ok=True)
    os.makedirs(bblib("cache"), exist_ok=True)
    os.system(f"cd {bblib()}; git init")
    
    update_token(token,"default")

    print(f"Initialized BioBricks library to {bblib()}.")
    return bblib()