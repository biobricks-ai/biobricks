import os, warnings
from pathlib import Path

def bblib(path=""):
    if 'BBLIB' in os.environ: return Path(os.environ['BBLIB']) / path
    raise Exception(f"""'BBLIB' env not available.
    Set your BBLIB environmental variable to use biobricks. eg:
    `os.environ['BBLIB']=/some/path`""")