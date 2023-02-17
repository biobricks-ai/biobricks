import sys
import os
import biobricks as bb
import click
from logger import logger

@click.group()
def cli():
    pass

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
