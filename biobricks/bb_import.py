from biobricks import bblib, pull
import pathlib as pl

def bb_import(brick,org="biobricks-ai",location=".bb"):
    pull(brick,org)
    
    brickdir : pl.Path = bblib() / org / brick

    orgdir : pl.Path = pl.Path(location) / org 
    orgdir.mkdir(exist_ok=True,parents=True)

    localdir = orgdir / brick
    localdir.symlink_to(brickdir,target_is_directory=True)