import sys, os
import biobricks as bb
import click, cloup, pkg_resources, requests
from .logger import logger
from pathlib import Path
from .config import read_config, write_config, init_bblib
from .checks import check_token
from .brick import Brick
from .local_bb import LocalBB

@cloup.group('biobricks')
def cli():
    pass

class Sect:
    GLOBAL = cloup.Section('GLOBAL: modify global config and installed bricks')
    BRICK = cloup.Section('LOCAL: build new bricks and manage their dependencies')

@cli.command(help="configure brick path and token",section=Sect.GLOBAL)
@click.option("--bblib", default=None, type=click.Path(), help="path to store bricks")
@click.option("--token", default=None, help="biobricks.ai/token auth token")
@click.option("--overwrite", default=False, help="overwrite existing config?")
def configure(bblib, token, overwrite):

    path = Path.home().joinpath(".biobricks")
    config = read_config()

    # CHECK IF CONFIG WILL OVERWRITE EXISTING
    msg = click.style("WARNING: overwrite existing config?", fg="red")
    if path.exists() and not overwrite and not click.confirm(msg):
        sys.exit(0)
    
    # EMAIL PROMPT 
    email = click.prompt("Choose Email", type=click.Path())

    # BBLIB PROMPT - DEFAULT TO EXISTING
    conmsg = lambda: f"use current BBLIB '{bblib or config['BBLIB']}'?"
    if not bblib and config.keys() >= {"BBLIB"} and click.confirm(conmsg(), default=True):
        bblib = config["BBLIB"]
    elif not bblib:
        bblib = click.prompt("Choose path to store bricks", type=click.Path())

    # TOKEN PROMPT - DEFAULT TO EXISTING AND THEN FREE TOKEN
    deftoken = "skip for temporary token"
    conmsg = f"use current token defined at '{path}'?"
    if not token and config.keys() >= {"TOKEN"} and click.confirm(conmsg):
        token = config["TOKEN"]
    elif not token:
        msg = "Copy token from biobricks.ai/token"
        token = click.prompt(msg, hide_input=True, default = deftoken)

    # VALIDATE TOKEN    
    while token != deftoken and not check_token(token, silent=True):
        click.echo(click.style("invalid token. check your token at https://biobricks.ai/token", fg="red"))
        token = click.prompt("Input a token from biobricks.ai/token",hide_input=True, default=deftoken)
    token = "VQF6Q2U-NKktZ31ioVYa9w" if token == deftoken else token

    # write configuration
    config = { "BBLIB": bblib, "TOKEN": token, "EMAIL": email }
    write_config(config)

    # initialize bblib
    bblib = init_bblib()

    msg = f"Done! BioBricks has BBLIB {bblib} and config {path}"
    click.echo(click.style(msg, fg="green"))

@cli.command(help="Install a data dependency", section=Sect.GLOBAL)
@click.argument("ref",type=str)
def install(ref):
    return Brick.Resolve(ref, force_remote=True).install()

@cli.command(help="Uninstall a data dependency", section=Sect.GLOBAL)
@click.argument("ref",type=str)
def uninstall(ref):
    return Brick.Resolve(ref).uninstall()

@cli.command(help="Initialize a .bb directory for data dependencies",
             section=Sect.BRICK)
def init():
    location = ".bb"
    dotbb = Path(location)
    if dotbb.exists():
        return
    dotbb.mkdir()
    
    with open(dotbb / ".gitignore", "w") as f: 
        f.write("/*/") # ignore all subdirectories
        
    # create file dotbb/dependencies.txt with no contents
    with open(dotbb / "dependencies.txt", "w") as f: 
        pass
    

def local_bblib():
    return Path(".bb")

def check_has_local_bblib():
    if not local_bblib().exists():
        raise Exception(".bb not found. run `biobricks init` first.")

@cli.command(name="add", help="Import a data dependency", section=Sect.BRICK)
@click.argument("ref",type=str)
def add(ref):
    check_has_local_bblib()
    localbb = LocalBB.FromPath(os.getcwd())
    localbb.add_dependency(ref)
    
@cli.command(name="pull", help="install local dependencies", section=Sect.BRICK)
def pull():
    check_has_local_bblib()
    lbb = LocalBB.FromPath(os.getcwd())
    lbb.install_dependencies()
    
@cli.command(help="Show the status of the local brick",
    section=Sect.BRICK)
def status():
    click.echo("BBLIB: " + str(bb.bblib()))
    # print the dependencies file
    with open(local_bblib() / "dependencies.txt", "r") as f:
        click.echo(f.read())
        
@cli.command(help="Get version and check for updates", section=Sect.GLOBAL)
def version():
    current_version = pkg_resources.get_distribution('biobricks').version
    response = requests.get('https://pypi.org/pypi/biobricks/json')
    latest_version = response.json()['info']['version']
    if current_version != latest_version:
        click.echo(f"\nA new version ({latest_version}) of biobricks is available. " 
              f"\nPlease upgrade using 'pip install --upgrade biobricks'\n")
    else:
        click.echo(f"biobricks version {current_version} is up to date.")
    
if __name__ == "__main__":
    cli()