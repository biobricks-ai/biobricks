import biobricks.checks
import biobricks.config
from biobricks.logger import logger


from dataclasses import dataclass
import requests, threading, time, shutil, os
import signal
from tqdm import tqdm
from pathlib import Path

def signal_handler(signum, frame, interrupt_event):
    interrupt_event.set()
    logger.info("Interrupt signal received. Attempting to terminate downloads gracefully...")

class PositionManager:
    def __init__(self):
        self.available_positions = []
        self.lock = threading.Lock()
        self.max_position = 0

    def get_position(self):
        with self.lock:
            if self.available_positions:
                return self.available_positions.pop(0)
            else:
                self.max_position += 1
                return self.max_position

    def release_position(self, position):
        with self.lock:
            self.available_positions.append(position)
            self.available_positions.sort()

class DownloadThread(threading.Thread):
    
    def __init__(self, url, total_progress_bar, path, headers, position_manager, semaphore, interrupt_event):
        super(DownloadThread, self).__init__()
        self.url = url
        self.total_progress_bar = total_progress_bar
        self.path = path
        self.headers = headers
        self.position_manager = position_manager
        self.semaphore = semaphore
        self.interrupt_event = interrupt_event

    def run(self):
        position = self.position_manager.get_position()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = requests.get(self.url, stream=True, headers=self.headers)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024

            with tqdm(total=total_size, unit='iB', unit_scale=True, disable=False, desc=str(self.path), position=position, leave=False) as progress:
                with open(self.path, 'wb') as file:
                    for data in response.iter_content(chunk_size=block_size):
                        if self.interrupt_event.is_set():  # Check if the thread should stop
                            logger.info(f"Stopping download of {self.url}")
                            return  # Exit the thread gracefully
                        if data:
                            file.write(data)
                            progress.update(len(data))
                            self.total_progress_bar.update(len(data))
        finally:
            self.semaphore.release()  # Release the semaphore when the thread is done
            self.position_manager.release_position(position)

@dataclass
class DownloadManager:
    skip_existing: bool = False
    progress_bar : tqdm = None
    active_threads : int = 0
    interrupt_event : threading.Event = threading.Event()
    
    def download_files(self, urls, paths, total_size, max_threads=4):
        signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, self.interrupt_event))

        self.progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, position=0, desc="Overall Progress")
        position_manager = PositionManager()
        semaphore = threading.Semaphore(max_threads)
        threads = []

        for url, path in zip(urls, paths):
            semaphore.acquire()  # Block until a semaphore permit is available
            if self.interrupt_event.is_set():
                logger.info("Download process interrupted. Waiting for ongoing downloads to complete...")
                semaphore.release()
                break
            thread = DownloadThread(url, self.progress_bar, path, {'BBToken': biobricks.config.token()}, position_manager, semaphore, self.interrupt_event)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.progress_bar.close()
        print(f"\n{len(paths)} files downloaded successfully!")

        
class DVCFetcher:
    
    def __init__(self, remote_url_prefix: str = 'https://dvc.biobricks.ai/files/md5/'):
        self.cache_path = biobricks.config.bblib() / "cache"
        self.remote_url_prefix: str = remote_url_prefix

    def _remote_url_to_cache_path(self, remote_url):
        return self.cache_path / remote_url.split('/')[-2] / remote_url.split('/')[-1]
    
    def _md5_to_remote_url(self, md5):
        return self.remote_url_prefix + md5[:2] + "/" + md5[2:]

    # TODO - this should have a better solution for error handling. What if the internet goes out? What if it's a completely wrong file?
    def _expand_outdir(self, remote_url, path : Path) -> list[dict]:
        """Returns a list of (md5,path) tuples for a given directory-out, skips on error."""
        try:
            with requests.get(remote_url, headers={'BBToken': biobricks.config.token()}, stream=True) as r:
                r.raise_for_status() 
                return [{'md5': o['md5'], 'path': path / o['relpath']} for o in r.json()]
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Failed to fetch {remote_url}: {e}")  # Log the error
            return []  # Return an empty list to skip this directory-out
    
    def _find_all_dirouts(self, dir_outs = []) -> list[dict]:
        urls, paths = [], []
        
        while dir_outs:
            current_dir_out = dir_outs.pop()
            current_dir_path = Path(current_dir_out['path'])
            expanded_outs = self._expand_outdir(self._md5_to_remote_url(current_dir_out['md5']), current_dir_path)

            # Separate file and directory outputs
            file_outs = [out for out in expanded_outs if not out['md5'].endswith('.dir')]
            more_dir_outs = [out for out in expanded_outs if out['md5'].endswith('.dir')]

            # Update lists with file outputs
            urls.extend(self._md5_to_remote_url(out['md5']) for out in file_outs)
            paths.extend(out['path'] for out in file_outs)

            # Add new directory outputs to be processed
            dir_outs.extend(more_dir_outs)
        
        return urls, paths
    
    def _link_cache_to_brick(self, cache_path, brick_path):
        "create a symlink from cache_path to brick_path, copy it if symlinks are not supported."
        if not cache_path.exists():
            logger.warning(f"cache file {cache_path} does not exist")
            return 
        
        brick_path.unlink(missing_ok=True)
        brick_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not biobricks.checks.can_symlink():
            logger.warning(f"you are not able to make symlinks cache-files will be copied to bricks. This is an inefficient use of disk space.")
            shutil.copy(cache_path, brick_path)
        else:
            os.symlink(cache_path, brick_path)
        
    def fetch_outs(self, brick, prefixes=['brick/'], force_redownload=False) -> tuple[list[dict], int]:
        dvc_lock = brick.get_dvc_lock()
        stages = [stage for stage in dvc_lock.get('stages', []).values()]
        all_outs = [out for stage in stages for out in stage.get('outs', [])]

        has_prefix = lambda x: any(x.get('path').startswith(prefix) for prefix in prefixes) or x.get('path') == 'brick'
        outs = [o for o in all_outs if has_prefix(o)]
        total_size = sum(o.get('size') for o in outs)
        
        dir_outs = [o for o in outs if o.get('md5').endswith('.dir')]
        dir_urls, dir_paths = self._find_all_dirouts(dir_outs)
        
        file_outs = [o for o in outs if not o.get('md5').endswith('.dir')]
        urls = dir_urls + [self._md5_to_remote_url(o.get('md5')) for o in file_outs]
        paths = dir_paths + [o.get('path') for o in file_outs]
        
        # download files
        cache_paths = [self._remote_url_to_cache_path(url) for url in urls]
        downloader = DownloadManager()
        
        if force_redownload:
            # If force_redownload is True, download all files
            to_download = list(zip(urls, cache_paths))
        else:
            # Check which files need to be downloaded
            to_download = [(url, cache_path) for url, cache_path in zip(urls, cache_paths) if not cache_path.exists()]
        
        if to_download:
            download_urls, download_paths = zip(*to_download) if to_download else ([], [])
            downloader.download_files(download_urls, download_paths, total_size)
        else:
            logger.info("All files already exist in cache. No downloads needed.")
        
        # build a symlink between each cache_path and its corresponding path
        brick_paths = [brick.path() / path for path in paths]
        for cache_path, brick_path in zip(cache_paths, brick_paths):
            self._link_cache_to_brick(cache_path, brick_path)
        
        return urls, paths, total_size
