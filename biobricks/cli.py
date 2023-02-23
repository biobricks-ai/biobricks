import sys
import os
import biobricks as bb
import click
from logger import logger
from pathlib import Path
import pathlib as pl, yaml, pkg_resources
from .config import read_config, write_config, init_bblib
from .checks import check_token
from .brick import Brick

@click.group()
def cli():
    pass

@cli.command(help="configure biobricks with a token and filesystem path")
def configure():

    path = Path.home().joinpath(".biobricks")
    config = {}

    if path.exists():
        config = read_config()
        if not click.confirm(click.style("WARNING: overwrite existing config?", fg="red")): sys.exit(0)
    
    # get bblib (default to existing bblib)
    if config.keys() >= {"BBLIB"} and click.confirm(f"use current BBLIB '{config['BBLIB']}'?", default=True):
        bblib = config["BBLIB"]
    else:
        bblib = click.prompt("Choose path to store bricks", type=click.Path())

    # initialize credentials (default to existing token)
    deftoken = "skip to use free token"
    if config.keys() >= {"TOKEN"} and click.confirm(f"use current token (see {path})?"):
        token = config["TOKEN"]
    else:
        token = click.prompt("what is your biobricks.ai/token?", hide_input=True, default = deftoken)
    
    while token != deftoken and not check_token(token, silent=True):
        click.echo(click.style("invalid token. check your token at https://biobricks.ai/token", fg="red"))
        token = click.prompt("what is your biobricks.ai token?",hide_input=True, default=deftoken)
    token = "VQF6Q2U-NKktZ31ioVYa9w" if token == deftoken else token
    click.echo()

    # write configuration
    config = { "BBLIB": bblib, "TOKEN": token }
    write_config(config)

    # initialize bblib
    bblib = init_bblib()

    msg = f"Done! BioBricks has BBLIB {bblib} and config {path}"
    click.echo(click.style(msg, fg="green"))


@cli.command(help="Initialize a .bb directory for data dependencies")
def init():
    location = ".bb"
    dotbb = pl.Path(location)
    if dotbb.exists():
        return
    dotbb.mkdir()
    
    with open(dotbb / ".gitignore", "w") as f: 
        f.write("/*/") # ignore all subdirectories

@cli.command(name="import",help="Import a data dependency into the .bb directory")
def import_(ref):
    location = ".bb"
    if(Path(location).exists() == False):
        raise Exception(".bb not found. run `biobricks init` first.")
    
    brick : Brick = install(ref) 
    
    localpath = Path(location) / brick.urlpath()
    localpath.mkdir(parents=True, exist_ok=True)

    brick.path().symlink_to(localpath, target_is_directory=True)

    # write a line to the dependencies file recording this import
    with open(pl.Path(location) / "dependencies.txt", "a") as f:
        f.write(f"{brick.urlpath()}\t{brick.commit}")


@cli.command(help="Install a data dependency into $BBLIB")
@click.argument("ref",type=str)
def install(ref):
    return Brick.Resolve(ref, force_remote=True).install()

@cli.command(help="Show the status of BBLIB")
def status():
    print("BBLIB: " + str(bb.bblib()))

if __name__ == "__main__":
    cli()
