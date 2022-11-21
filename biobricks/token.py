import os, pathlib, json, typing

from warnings import warn
from .bblib import bblib

def token(name:typing.AnyStr='default'): 
    if not os.path.exists(bblib('credentials.json')): return None
    text = pathlib.Path(bblib('credentials.json')).read_text()
    return json.loads(text)[name]

def token_init(name,token):
    cfg = { 'default': token  }
    bblib('credentials.json').write_text(json.dumps(cfg))   
    