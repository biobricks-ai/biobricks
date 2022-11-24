import os, pathlib, json, typing, urllib

from .bblib import bblib

def token(name:typing.AnyStr='default'): 
    if not os.path.exists(bblib('credentials.json')): return None
    text = pathlib.Path(bblib('credentials.json')).read_text()
    return json.loads(text)[name]

def update_token(token,name="default"):
    cfg = { name : token  }
    bblib('credentials.json').write_text(json.dumps(cfg))   

def check_token(token):
    """verify that the token is a valid biobricks.ai token"""
    url = f"https://members.biobricks.ai/token/is_valid?token={token}"
    try:
        is_valid = json.loads(urllib.request.urlopen(url).read())
        if not is_valid: raise ValueError(f"""invalid token. 
            - update token with `biobricks.update_token`.
            - get your token at https://members.biobricks.ai""")
    except Exception as e:
        raise Exception(f"error validating token.") from e
    
