from biobricks import bblib
import types, pyarrow.parquet as pq, re
from pathlib import Path
from logger import logger

# TODO add nested namespace support
def load(brick,org="biobricks-ai"):
    bdir = bblib() / org / brick
    if not bdir.exists(): 
        raise Exception(f"no path '{bdir}' try `biobricks.pull({brick})`")
       
    def dirns(dir: Path):
        filter = lambda d: d.name.endswith('.parquet')
        paths = [d for d in dir.rglob('*') if filter(d)]
        namespace = types.SimpleNamespace()
        pkey = lambda p: re.sub(r'[.-]','_',p)
        for p in paths:
            path = p.relative_to(dir)
            logger.info(f"loading {path}...")
            current = namespace
            for part in path.parts:
                key = pkey(part)
                if not hasattr(current, key) and part.endswith('.parquet'):
                    setattr(current, key[:-8], pq.read_table(str(p)))
                elif not hasattr(current, key):
                    setattr(current, key, types.SimpleNamespace())
                    current = getattr(current, key)
                elif hasattr(current, key):
                    current = getattr(current, key)
        logger.info(f"loaded {len(paths)} tables from {dir}")
        return namespace

    ns1 = dirns(bdir / 'data')
    ns2 = dirns(bdir / 'brick')
    result = {**ns2.__dict__, **ns1.__dict__}
    return types.SimpleNamespace(**result)