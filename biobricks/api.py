from .brick import Brick
from .cli import cli
from .checks import check_configured
from . import auth
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
    """List the bricks available on github.com/biobricks-ai (including private repos if authenticated)"""
    check_configured()

    headers = {"Accept": "application/vnd.github+json"}
    github_token = auth.get_github_token()
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    # Paginate through all repos
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/orgs/biobricks-ai/repos?per_page=100&page={page}",
            headers=headers
        )
        repos = json.loads(r.text)
        if not repos:
            break
        for repo in repos:
            yield repo["name"]
        page += 1