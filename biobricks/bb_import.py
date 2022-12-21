from biobricks import bblib, pull
import pathlib as pl, pkg_resources, yaml

def bb_init(location=".bb"):

    dotbb = pl.Path(location)
    if dotbb.exists(): return
    dotbb.mkdir()
    
    # get package verfsion
    config = {"version":pkg_resources.get_distribution("biobricks").version}
    with open(dotbb / "config", "w") as f: 
        yaml.dump(config,f)
    
    with open(dotbb / ".gitignore", "w") as f: 
        f.write("/*/") # ignore all subdirectories
        

def bb_import(brick,org="biobricks-ai",location=".bb"):

    if(pl.Path(location).exists() == False):
        raise Exception(".bb not found. run `bb init` first.")
    
    pull(brick,org)
    brickdir : pl.Path = bblib() / org / brick

    orgdir : pl.Path = pl.Path(location) / org 
    orgdir.mkdir(exist_ok=True,parents=True)

    localdir = orgdir / brick
    localdir.symlink_to(brickdir,target_is_directory=True)

    # write a line to the config file recording this import
    with open(pl.Path(location) / "config", "a") as f:
        f.write(f"{org}/{brick}")
    
        
