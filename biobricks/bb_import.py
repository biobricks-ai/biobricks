from biobricks import bblib
import pathlib as pl, pkg_resources, yaml
        
    
def bb_install(location=".bb"):
    """install all the bricks in the .bb directory"""
    # TODO this is broken
    return None

#     with open(pl.Path(location) / "config") as f:
#         for line in f:
#             brick = Brick.fromurl(line)
#             brick.install()
