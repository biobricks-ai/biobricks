from biobricks import bblib
import types, pyarrow.parquet as pq

def load(brick,org="biobricks-ai"):
    bdir = bblib() / org / brick
    if not bdir.exists(): 
        raise Exception(f"no path '{bdir}' try `biobricks.pull({brick})`")
    
    pathD = list(bdir.glob('data/*.parquet'))
    pathB = list(bdir.glob('brick/*.parquet'))
    paths = pathB + pathD

    tbls = dict([(x.stem,pq.read_table(x)) for x in paths])
    return types.SimpleNamespace(**tbls)