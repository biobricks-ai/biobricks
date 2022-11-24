from biobricks import bblib, token, check_token
from subprocess import run, DEVNULL
import os, urllib.request as request, functools, dvc.api

def check_url_available(url):
    try:
        code = request.urlopen(url).getcode()
        if code!=200:
            raise Exception(f"{url} not available")
    except Exception as e:
        raise Exception(f"{url} not available") from e

def pull(brick,org="biobricks-ai"):
    repo = f"{org}/{brick}"
    url  = "https://github.com/"+repo
    check_url_available(url)
    check_token(token())

    bblib(org).mkdir(exist_ok=True)    
    cmd = functools.partial(run,shell=True,stdout=DEVNULL,stderr=DEVNULL)
    cmd(f"git submodule add {url} {repo}",cwd=bblib())
    
    rsys = functools.partial(cmd,cwd=bblib(repo))
    rsys("dvc cache dir ../../cache")
    rsys("dvc config cache.shared group")
    rsys("dvc config cache.type symlink")
    rsys(f"git commit -m \"added {repo}\"")

    # SET UP BIOBRICKS.AI DVC REMOTE WITH AUTH
    rsys("dvc remote add -f biobricks.ai https://dvc.biobricks.ai")
    rsys("dvc remote modify --local biobricks.ai auth custom")
    rsys("dvc remote modify --local biobricks.ai custom_auth_header BBToken")
    rsys(f"dvc remote modify --local biobricks.ai password {token()}")

    fs = dvc.api.DVCFileSystem(bblib(repo))
    paths = fs.find("data",maxdepth=1) + fs.find("brick",maxdepth=1)
    parquet_paths = [x for x in paths if x.endswith('.parquet')]

    rsys(f"dvc pull {' '.join(parquet_paths)}")
    return True

def uninstall(brick,org="biobricks-ai"):
    "completely remove submodule (see https://stackoverflow.com/questions/1260748/how-do-i-remove-a-submodule)"
    repo = f"{org}/{brick}"
    
    os.system(f"cd {bblib()}; git rm -f {repo}")
    os.system(f"cd {bblib()}; rm -rf .git/modules/{repo}")
    os.system(f"cd {bblib()}; git config --remove-section submodule.{repo}")
    