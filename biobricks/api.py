from .brick import Brick
from .cli import cli
from .checks import check_configured

def load(brick):
    """Load a brick from the local filesystem"""
    check_configured()
    return Brick.Resolve(brick).load()

def install(brick):
    """Install a brick from a remote repository"""
    check_configured()
    return Brick.Resolve(brick).install()

def configure():
    """Configure biobricks globally"""
    return cli.config()
