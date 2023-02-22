import urllib.request as request
import json, urllib

def check_url_available(url):
    try:
        code = request.urlopen(url).getcode()
        if code!=200:
            raise Exception(f"{url} not available")
    except Exception as e:
        raise Exception(f"{url} not available") from e

def check_token(token, silent=False):
    """verify that the token is a valid biobricks.ai token"""
    url = f"https://biobricks.ai/token/is_valid?token={token}"
    is_valid = json.loads(urllib.request.urlopen(url).read())
    if not is_valid and not silent: 
        raise ValueError(f"Invalid token. Run `biobricks configure`")
    return is_valid