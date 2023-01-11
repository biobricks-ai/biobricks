from biobricks import bblib
import types, pyarrow.parquet as pq, re
from pathlib import Path
from logger import logger

def _buildns(paths):
    namespace = types.SimpleNamespace()
    pkey = lambda p: re.sub(r'[.-]','_',p)
    for p in paths:
        path = p.relative_to(dir)
        logger.info(f"loading {path}...")
        current = namespace
        for part in path.parts:
            key = pkey(part)
            if not hasattr(current, key) and part.endswith('.parquet'):
                setattr(current, key[:-8], pq.read_table(p))
            elif not hasattr(current, key):
                setattr(current, key, types.SimpleNamespace())
                current = getattr(current, key)
            elif hasattr(current, key):
                current = getattr(current, key)
    logger.info(f"loaded {len(paths)} tables")
    return namespace
    
def load(brick,org="biobricks-ai"):
    bdir = bblib() / org / brick
    if not bdir.exists(): 
        raise Exception(f"no path '{bdir}' try `biobricks.pull({brick})`")
       
    def list_parquet_subdirs(dir: Path):
        filter = lambda d: d.is_dir() and d.name.endswith('.parquet')
        return [d for d in dir.rglob('*') if filter(d)]

    pathD = list_parquet_subdirs(bdir / 'data')
    pathB = list_parquet_subdirs(bdir / 'brick')
    return _buildns(pathD + pathB)


