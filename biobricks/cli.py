import sys
import os
import biobricks as bb
import click
from logger import logger
from pathlib import Path
from .bblib import read_config, write_config, init_bblib, check_token

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
    bb.bb_init()

@cli.command(name="import",help="Import a data dependency into the .bb directory")
def import_(brick,org="biobricks-ai",location=".bb"):
    bb.bb_import(brick,org,location)

@cli.command(help="Install a data dependency into $BBLIB")
@click.argument('args', nargs=-1)
def install(args):
    bb.pull(*args)

@cli.command(help="Show the status of BBLIB")
def status():
    logger.info("BBLIB: " + str(bb.bblib()))

if __name__ == "__main__":
    cli()
