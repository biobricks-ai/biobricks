from .brick import Brick
from .cli import cli
from .checks import check_configured

def load(brick):
    """Load a brick from the local filesystem"""
    check_configured()
    return Brick.Resolve(brick).load()

def assets(brick):
    """List the paths of the assets of a brick"""
    check_configured()
    return [str(x) for x in Brick.Resolve(brick).assets()]

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
