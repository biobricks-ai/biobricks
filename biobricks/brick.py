import subprocess, functools, os, re, datetime, json
from subprocess import run, DEVNULL
import types, pyarrow.parquet as pq, re
from pathlib import Path
from .config import bblib, token
from .logger import logger
import os, urllib.request as request, functools, dvc.api
from urllib.parse import urlparse
import sys
from .checks import check_url_available, check_token, check_symlink_permission

class Brick:

    def __init__(self, remote, commit):
        self.remote = remote
        self.commit = commit
        self.name = remote.split("/")[-1]
    
    @staticmethod
    def FromURL(url):
        """Get the version of a brick from its git repo."""
        remote, commit = url.split("#")
        return Brick(remote, commit)

    @staticmethod
    def FromPath(path):
        """Get the version of a brick from its git repo."""
        bdir = bblib(path)
        gsys = functools.partial(subprocess.check_output, shell=True, cwd=bdir)
        commit = gsys("git rev-parse HEAD").decode().strip()
        remote = gsys("git config --get remote.origin.url").decode().strip()
        return Brick(remote, commit)

    @staticmethod
    def FromRemote(remote):
        """Get the version of a brick from its git repo."""
        try:
            logger.info(f"getting latest version of {remote}")
            commit = subprocess.check_output(f'git ls-remote "{remote}" HEAD', shell=True)
            commit = commit.decode().strip().split()[0]
            return Brick(remote, commit)
        except subprocess.CalledProcessError as e:
            logger.error(f"failed to get latest version of {remote}: {e}")
            raise RuntimeError(f"Failed to get the latest version of {remote}. Is {remote} a valid git repository?")


    @staticmethod
    def Resolve(ref:str, force_remote=False):
        """find all bricks matching ref. `ref` can be:
            - existing  name ie. 'tox21'
            - git-url syntax ie. 'https://github.com/biobricks-ai/tox21#commit'
        if `force_remote` is True then retrieve brick from remote repository"""
        
        # if name matches remote#commit then resolve from url        
        if re.match("^http.*[0-9a-f]{40}$",ref):
            return Brick.FromURL(ref)
        
        # if name matches remote then resolve from remote
        if re.match("^http.*$",ref):
            return Brick.FromRemote(ref)
        
        # otherwise resolve to https://github.com/biobricks-ai/<name>
        remote = f"https://github.com/biobricks-ai/{ref}"

        if force_remote: 
            return Brick.FromRemote(remote)

        # retrieve from library if it exists
        bricks = []
        bdir = bblib() / "biobricks-ai" / ref
        if bdir.exists():
            for bdir in (bblib() / "biobricks-ai" / ref).iterdir():
                logger.info(f"checking {bdir.name} for {ref}")
                # if the directory is a sha hash then add it to brick array
                if bdir.is_dir() and re.match("[0-9a-f]{40}$",bdir.name):
                    brick = Brick.FromPath(bdir)
                    if remote == brick.remote:
                        bricks.append(brick)
        
        # sort the bricks by their commit_date
        bricks.sort(key=lambda b: b.get_commit_date(), reverse=True)
        
        # pick the most recent one
        if len(bricks) > 0:
            return bricks[0]
        
        # if we can't find it in the library, then get the remote version
        return Brick.FromRemote(remote)


    def get_commit_date(self):
        """get the date of the commit"""
        gsys = functools.partial(subprocess.check_output, shell=True, cwd=self.path())
        date = gsys("git show -s --format=%ci").decode().strip()
        return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")

    def url(self):
        return f"{self.remote}#{self.commit}"
    
    def urlpath(self):
        return Path(urlparse(self.url()).path[1:])

    def path(self):
        return bblib() / self.urlpath() / self.commit

    def _relpath(self):
        "get the path to this brick relative to bblib"
        return self.urlpath() / self.commit

    def install(self):
        "install this brick"
        logger.info(f"running checks on brick")
        
        if bblib(self.commit).exists():
            logger.info(f"\033[91m{self.url}\033[0m already exists in BioBricks library.")
            return True
        
        check_url_available(self.remote)
        check_token(token())
        check_symlink_permission()

        cmd = functools.partial(run,shell=True,stdout=DEVNULL,stderr=DEVNULL)
        
        # old way - cmd(f"git submodule add {self.remote} {self.repo}",cwd=bblib())
        logger.info(f"git clone {self.remote} {self._relpath()} in {bblib()}")
        cmd(f"git clone {self.remote} {self._relpath()}", cwd = bblib())
        cmd(f"git checkout {self.commit}", cwd = self.path())

        logger.info(f"adding brick to dvc cache")
        rsys = functools.partial(cmd,cwd=self.path())
        rsys(f"dvc cache dir {bblib() / 'cache'}")
        rsys("dvc config cache.shared group")
        rsys("dvc config cache.type symlink")

        # SET UP BIOBRICKS.AI DVC REMOTE WITH AUTH
        logger.info(f"setting up credentials for dvc.biobricks.ai")
        rsys("dvc remote add -f biobricks.ai https://dvc.biobricks.ai")
        rsys("dvc remote modify --local biobricks.ai auth custom")
        rsys("dvc remote modify --local biobricks.ai custom_auth_header BBToken")
        rsys("dvc remote modify --local biobricks.ai read_timeout 300")
        rsys("dvc remote modify --local biobricks.ai connect_timeout 300")

        rsys(f"dvc remote modify --local biobricks.ai password {token()}")

        logger.info(f"discovering brick assets dvc.biobricks.ai")
        fs = dvc.api.DVCFileSystem(self.path())
        paths = fs.find("data",maxdepth=1) + fs.find("brick",maxdepth=1)
        parquet_paths = [x for x in paths if x.endswith('.parquet')]

        logger.info(f"pulling brick assets")
        # TODO dvc currently queries the cache which involves big md5 calculations
        # instead we should use the dvc api to pull the files directly
        run(f"dvc pull {' '.join(parquet_paths)}", cwd=self.path(), shell=True, stdout=sys.stderr)
        
        logger.info(f"\033[94m{self.url()}\033[0m succesfully downloaded to BioBricks library.")
        return self
    
    def load(self):
        "load this brick"
        bdir = self.path()
        if not bdir.exists(): 
            raise Exception(f"no path '{bdir}' try `biobricks install {self.url()}`")
        
        # get assets and strip .parquet from assets to make names
        assets = [Path(p) for p in self.assets()]
        names = [p.with_suffix('').name for p in assets]
        
        # make a simple namespace using names as keys and loading assets with pq.ParquetDataset
        ds = [pq.ParquetDataset(str(p)) for p in assets]
        return types.SimpleNamespace(**dict(zip(names, ds)))
    
    def assets(self):
        "get the assets for this brick"
        bdir = self.path()
        if not bdir.exists(): 
            raise Exception(f"no path '{bdir}' try `biobricks install {self.url()}`")
        
        def find_parquet_files(directory):
            if not directory.exists():
                return []
            for entry in os.scandir(directory):
                if entry.name.endswith('.parquet'):
                    yield entry.path
                elif entry.is_dir():
                    yield from find_parquet_files(Path(entry.path))
                
        return list(find_parquet_files(bdir / 'data')) + list(find_parquet_files(bdir / 'brick'))
    
    def uninstall(self):
        "uninstall this brick"
        os.rmdir(self.path())
        