import os, warnings
from pathlib import Path

def check_has_bblib():
    return 'BBLIB' in os.environ

def set_bblib(path):
    os.environ['BBLIB'] = str(path)

def bblib(path=""):
    if check_has_bblib(): return Path(os.environ['BBLIB']) / path
    raise Exception("""'BBLIB' env not available.
    Set your BBLIB environmental variable to use biobricks. eg:
    `os.environ['BBLIB']=/some/path`""")