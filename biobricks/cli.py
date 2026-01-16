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
from . import auth

@cloup.group('biobricks')
def cli():
    pass

class Sect:
    GLOBAL = cloup.Section('GLOBAL: modify global config and installed bricks')
    AUTH = cloup.Section('AUTH: authenticate with GitHub for private repositories')
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

# ============== AUTH COMMANDS ==============

@cli.command(name="auth", help="Authenticate with GitHub for private repositories", section=Sect.AUTH)
@click.option("--token", default=None, help="GitHub Personal Access Token (or use interactive login)")
@click.option("--device-flow", is_flag=True, help="Use browser-based OAuth login")
def auth_login(token, device_flow):
    """Authenticate with GitHub to access private BioBricks repositories."""
    if token:
        # Login with PAT
        try:
            user = auth.login_with_pat(token)
            click.echo(click.style(f"Authenticated as {user['login']}", fg="green"))

            # Check access to biobricks-ai org
            if auth.check_repo_access(token):
                click.echo(click.style("Access to biobricks-ai private repos confirmed.", fg="green"))
            else:
                click.echo(click.style("Warning: Token may not have access to biobricks-ai private repos.", fg="yellow"))
        except ValueError as e:
            click.echo(click.style(f"Authentication failed: {e}", fg="red"))
            sys.exit(1)
    elif device_flow:
        # Browser-based OAuth login
        try:
            user = auth.login_with_device_flow()
            click.echo(click.style(f"\nAuthenticated as {user['login']}", fg="green"))
        except (TimeoutError, PermissionError, RuntimeError) as e:
            click.echo(click.style(f"Authentication failed: {e}", fg="red"))
            sys.exit(1)
    else:
        # Interactive: prompt for token or use device flow
        click.echo("BioBricks GitHub Authentication")
        click.echo("=" * 40)
        click.echo("\nOptions:")
        click.echo("  1. Enter a GitHub Personal Access Token")
        click.echo("  2. Login via browser (OAuth)\n")

        choice = click.prompt("Choose option", type=click.Choice(['1', '2']), default='2')

        if choice == '1':
            click.echo("\nCreate a token at: https://github.com/settings/tokens")
            click.echo("Required scope: 'repo' (Full control of private repositories)\n")
            pat = click.prompt("Enter your GitHub Personal Access Token", hide_input=True)
            try:
                user = auth.login_with_pat(pat)
                click.echo(click.style(f"\nAuthenticated as {user['login']}", fg="green"))
            except ValueError as e:
                click.echo(click.style(f"Authentication failed: {e}", fg="red"))
                sys.exit(1)
        else:
            try:
                user = auth.login_with_device_flow()
                click.echo(click.style(f"\nAuthenticated as {user['login']}", fg="green"))
            except (TimeoutError, PermissionError, RuntimeError) as e:
                click.echo(click.style(f"Authentication failed: {e}", fg="red"))
                sys.exit(1)


@cli.command(name="auth-status", help="Show GitHub authentication status", section=Sect.AUTH)
def auth_status():
    """Show current GitHub authentication status."""
    status = auth.get_auth_status()

    if status["authenticated"]:
        click.echo(click.style("GitHub: Authenticated", fg="green"))
        if status.get("user"):
            click.echo(f"  User: {status['user']}")
        if status.get("valid") is False:
            click.echo(click.style("  Warning: Token may be expired or invalid", fg="yellow"))
        if status.get("has_refresh_token"):
            click.echo("  Refresh token: Available")
    else:
        click.echo(click.style("GitHub: Not authenticated", fg="yellow"))
        click.echo("  Run 'biobricks auth' to authenticate")


@cli.command(name="auth-logout", help="Remove GitHub authentication", section=Sect.AUTH)
def auth_logout():
    """Remove stored GitHub credentials."""
    auth.clear_github_token()
    click.echo(click.style("GitHub authentication removed.", fg="green"))


# ============== BRICK COMMANDS ==============

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