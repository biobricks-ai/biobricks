from .config import bblib, token
from .logger import logger
import os
import shutil
import requests
import biobricks.checks
from pathlib import Path
from tqdm import tqdm  # Import tqdm for the progress bar

from dataclasses import dataclass, field

@dataclass
class Downloader:
    remote_url_prefix: str = field(default = 'https://dvc.biobricks.ai/files/md5/')

    def _md5_to_remote_url( self, md5 ):
        return self.remote_url_prefix + md5[:2] + "/" + md5[2:]

    def _download_outdir(self, url, dest_path: Path):
        with requests.get(url, headers={'BBToken': token()}, stream=True) as r:
            r.raise_for_status()
            for o in r.json():
                self.download_out(o['md5'], dest_path / o['relpath'])
                    
    def _download_outfile(self, url, path: Path, bytes=None):

        with requests.get(url, headers={'BBToken': token()}, stream=True) as r:
            r.raise_for_status()
            total_size = bytes if bytes else int(r.headers.get('content-length', 0))
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=f"Downloading file")
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress_bar.update(len(chunk))
            progress_bar.close()
            if total_size != 0 and progress_bar.n != total_size:
                logger.error("ERROR, something went wrong")
        

    def download_out(self, md5, dest: Path, url_prefix="https://dvc.biobricks.ai/files/md5/", bytes=None):
        
        # make parent directories
        dest.parent.mkdir(parents=True, exist_ok=True)
        cache_path = bblib() / 'cache' / md5[:2] / md5[2:]
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        remote_url = self._md5_to_remote_url(md5)

        if md5.endswith('.dir'):
            logger.info(f"downloading directory {remote_url} to {dest}")
            return self._download_outdir(remote_url, dest)

        if not cache_path.exists():
            logger.info(f"downloading file {remote_url} to {cache_path}")
            self._download_outfile(remote_url, cache_path, bytes)

        dest.unlink(missing_ok=True) # remove the symlink if it exists
        if not biobricks.checks.can_symlink():
            logger.warning(f"you are not able to make symlinks cache-files will be copied to bricks. This is an inefficient use of disk space.")
            shutil.copy(cache_path, dest)
        else:
            os.symlink(cache_path, dest)

    def download_by_prefix(self, outs, prefix, path):
        brick_outs = [out for out in outs if out.get('path').startswith(prefix)]
        for out in brick_outs:
            md5 = out.get('md5')
            relpath = out.get('path')
            dest_path = path / relpath
            self.download_out(md5, dest_path)
    
