from .brick import Brick
from .cli import cli
from .checks import check_configured
import requests, json 

def assets(brick):
    """List the paths of the assets of a brick"""
    check_configured()
    return Brick.Resolve(brick).assets()

def path(brick):
    check_configured()
    return Brick.Resolve(brick).path()

def install(brick):
    """Install a brick from a remote repository"""
    check_configured()
    return Brick.Resolve(brick).install()

def configure():
    """Configure biobricks globally"""
    return cli.config()
    
def ls_remote():
    """List the bricks available on github.com/biobricks-ai"""
    check_configured()
    r = requests.get("https://api.github.com/users/biobricks-ai/repos")
    repos = json.loads(r.text)
    for repo in repos:
        yield repo["name"]