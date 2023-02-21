import subprocess, functools
from bblib import bblib

class Brick:

    def __init__(self, remote, commit):
        self.remote = remote
        self.commit = commit
    
    def url(self):
        return f"{self.remote}#{self.commit}"
    
    @staticmethod
    def fromurl(url):
        """Get the version of a brick from its git repo."""
        remote, commit = url.split("#")
        return Brick(remote, commit)
        
    @staticmethod
    def fromlib(brick, org="biobricks-ai"):
        """Get the version of a brick from its git repo."""
        bdir = bblib() / org / brick
        gsys = functools.partial(subprocess.check_output, shell=True, cwd=bdir)
        commit = gsys("git rev-parse HEAD").decode().strip()
        remote = gsys("git config --get remote.origin.url").decode().strip()
        return Brick(remote, commit)

    def install():
        "install this brick"
        orgdir = bblib() / org
        orgdir.mkdir(exist_ok=True, parents=True)
        subprocess.run(f"git clone {self.remote}", cwd = bblib() / org)
        subprocess.run(f"git checkout {self.commit}", cwd = bblib() / org / brick)