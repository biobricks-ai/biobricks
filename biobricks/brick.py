import subprocess, functools, os, re, datetime, json
from subprocess import run, DEVNULL
import types
from pathlib import Path
from .config import bblib, token
from .logger import logger
import os, urllib.request as request, functools, shutil, yaml
from .downloader import download_out
from urllib.parse import urlparse
import sys
from .checks import check_url_available, check_token, check_symlink_permission, check_safe_git_repo

class Brick:
    
    ALLOWED_FILETYPES = ['.parquet','.sqlite','.hdt']
    
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
        
        is_safe = check_safe_git_repo(bdir)
        if not is_safe:
            subprocess.check_call(['git', 'config', '--global', '--add', 'safe.directory', bdir])
            
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
                logger.debug(f"checking {bdir.name} for {ref}")
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
        
        logger.info(f"git clone {self.remote} {self._relpath()} in {bblib()}")
        cmd(f"git clone {self.remote} {self._relpath()}", cwd = bblib())
        cmd(f"git checkout {self.commit}", cwd = self.path())

        outs = []
        with open(self.path() / "dvc.lock") as f:
            dvc_lock = yaml.safe_load(f)
            stages = [stage for stage in dvc_lock.get('stages', []).values()]
            outs = [out for stage in stages for out in stage.get('outs', [])]
        
        brick_outs = [out for out in outs if out.get('path').startswith('brick')]
        for out in brick_outs:
            md5 = out.get('md5')
            relpath = out.get('path')
            dest_path = self.path() / relpath
            download_out(md5, dest_path)
            
        logger.info(f"\033[94m{self.url()}\033[0m succesfully downloaded to BioBricks library.")
        return self
    
    def assets(self):
        """Get the assets for this brick."""
        brick_dir = self.path()
        
        is_safe = check_safe_git_repo(self.path())
        
        if not is_safe:
            subprocess.check_call(['git', 'config', '--global', '--add', 'safe.directory', brick_dir])
        
        if not brick_dir.exists():
            raise Exception(f"No path '{brick_dir}'. Try `biobricks install {self.url()}`")

        def collect_allowed_files(target_dir, startdir):
            """Recursively collect files with allowed extensions."""
            if not target_dir.exists():
                return {}
            
            collected_files = {}
            for entry in os.scandir(target_dir):
                rel_path = os.path.relpath(entry.path, start = startdir)
                if any(entry.name.endswith(ext) for ext in Brick.ALLOWED_FILETYPES):
                    collected_files[rel_path] = entry.path
                elif entry.is_dir():
                    collected_files.update(collect_allowed_files(Path(entry.path), startdir))
            
            return collected_files

        brick_assets_dict = collect_allowed_files(brick_dir / 'brick', startdir = brick_dir / 'brick')
        data_assets_dict = collect_allowed_files(brick_dir / 'data', startdir = brick_dir / 'data')
        assets_dict = {**brick_assets_dict, **data_assets_dict}

        # Post-process the keys
        process = lambda key: key.replace('/', '_').replace('\\', '_').replace('.', '_')
        assets_dict = {process(key): value for key, value in assets_dict.items()}

        
        return types.SimpleNamespace(**assets_dict)

    def uninstall(self):
        "uninstall this brick"
        
        if not os.path.exists(self.path()):
            raise Exception(f"The brick {self.url()} is not installed.")

        try:
            shutil.rmtree(self.path())
        except Exception as e:
            raise Exception(f"Error occurred while removing directory: {e}")
        