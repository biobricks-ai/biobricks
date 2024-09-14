import sys, os, types
import biobricks as bb
import click, cloup, requests
from pathlib import Path
from importlib import metadata

from .logger import logger
from .config import biobricks_config_path, read_config, write_config, init_bblib
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
@click.option("--interactive", default=True, help="run configure interactively?")
def configure(bblib, token, overwrite, interactive):
    
    if not interactive:
        config = { "BBLIB": f"{bblib}", "TOKEN": token }
        write_config(config)
        init_bblib()
        return

    path = biobricks_config_path()
    config = read_config()

    # CHECK IF CONFIG WILL OVERWRITE EXISTING
    msg = click.style("WARNING: overwrite existing config?", fg="red")
    if path.exists() and not overwrite and not click.confirm(msg):
        sys.exit(0)

    # VALIDATE TOKEN    
    token = click.prompt("Input a token from biobricks.ai/token",hide_input=True)
    while not check_token(token, silent=True):
        click.echo(click.style("invalid token. check your token at https://biobricks.ai/token", fg="red"))
        token = click.prompt("Input a token from biobricks.ai/token",hide_input=True)
    
    # BBLIB PROMPT - DEFAULT TO EXISTING
    conmsg = lambda: f"use current BBLIB '{bblib or config['BBLIB']}'?"
    if not bblib and config.keys() >= {"BBLIB"} and click.confirm(conmsg(), default=True):
        bblib = config["BBLIB"]
    elif not bblib:
        bblib = click.prompt("Choose path to store bricks", type=click.Path())

    # write configuration
    config = { "BBLIB": bblib, "TOKEN": token }
    write_config(config)

    # initialize bblib
    bblib = init_bblib()

    msg = f"Done! BioBricks has BBLIB {bblib} and config {path}"
    click.echo(click.style(msg, fg="green"))

@cli.command(help="Install a data dependency", section=Sect.GLOBAL)
@click.argument("ref", type=str)
@click.option('--force', is_flag=True, help="Force redownload of the brick and all its assets")
def install(ref, force):
    try:
        brick = Brick.Resolve(ref, force_remote=True)
        result = brick.install(force_redownload=force)
        if result is True:
            click.echo(f"Brick '{ref}' is already installed.")
        else:
            click.echo(f"Successfully installed brick '{ref}'.")
    except Exception as e:
        click.echo(f"Error occurred while installing '{ref}': {e}", err=True)

@cli.command(help="Uninstall a data dependency", section=Sect.GLOBAL)
@click.argument("ref", type=str)
def uninstall(ref):
    brick = Brick.Resolve(ref)

    # Confirmation prompt
    if click.confirm(f"Are you sure you want to uninstall the brick '{ref}'?"):
        try:
            brick.uninstall()
            click.echo(f"Successfully uninstalled '{ref}'.")
        except Exception as e:
            click.echo(f"Error occurred while uninstalling '{ref}': {e}", err=True)
    else:
        click.echo("Uninstallation cancelled.")

@cli.command(help="List assets in a data dependency", section=Sect.GLOBAL)
@click.argument("ref",type=str)
def assets(ref):
    assets : types.SimpleNamespace = Brick.Resolve(ref).assets()
    for key, value in vars(assets).items():
        click.echo(f"{key}: {value}")

@cli.command(help="Initialize a .bb directory for data dependencies", section=Sect.BRICK)
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

@cli.command(name="remove", help="Remove a data dependency", section=Sect.BRICK)
@click.argument("ref",type=str)
def remove(ref):
    check_has_local_bblib()
    localbb = LocalBB.FromPath(os.getcwd())
    localbb.remove_dependency(ref)
    
@cli.command(name="pull", help="install local dependencies", section=Sect.BRICK)
def pull():
    check_has_local_bblib()
    lbb = LocalBB.FromPath(os.getcwd())
    lbb.install_dependencies()
    
@cli.command(help="Show the status of the local brick", section=Sect.BRICK)
def status():
    click.echo("BBLIB: " + str(bb.bblib()))
    # print the dependencies file
    with open(local_bblib() / "dependencies.txt", "r") as f:
        click.echo(f.read())
        
@cli.command(help="Get version and check for updates", section=Sect.GLOBAL)
def version():
    current_version = metadata.version('biobricks')
    response = requests.get('https://pypi.org/pypi/biobricks/json')
    latest_version = response.json()['info']['version']
    if current_version != latest_version:
        logger.warning(f"upgrade to {latest_version} with 'pip install --upgrade biobricks'")
    click.echo(f"local_version: {current_version}\nlatest_version: {latest_version}")
    
if __name__ == "__main__":
    cli()