import urllib.request as request
import json, urllib
import os, tempfile, uuid, requests
import subprocess
from pathlib import Path

def check_safe_git_repo(git_repo_path):
    "every biobrick needs to be a safe git directory"
    try:
        raw_safe_dirs = subprocess.check_output(['git', 'config', '--global', '--get-regexp', 'safe.directory']).decode().strip()
    except subprocess.CalledProcessError as e:
        raw_safe_dirs = ""
    safe_dirs = [line.split(' ')[1] for line in raw_safe_dirs.split('\n') if line.strip() != '']
    # Normalize path to string for comparison
    normalized_path = str(Path(git_repo_path).resolve())
    return normalized_path in safe_dirs or str(git_repo_path) in safe_dirs
        
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

def can_symlink():
    try:
        src = tempfile.NamedTemporaryFile()
        dst = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        os.symlink(src.name, dst)
        os.remove(dst)
        src.close()
        return True
    except Exception as e:
        return False

def check_configured():
    """check that biobricks is configured"""
    try:
        from .config import read_config, check_has_bblib
        if not read_config(): raise Exception("no config")
        if not check_has_bblib(): raise Exception("no bblib")
        if not check_token(read_config()["TOKEN"], silent=True): raise Exception("invalid token")
        return True
    except Exception as e:
        raise Exception("biobricks not configured. run `biobricks configure`") from e