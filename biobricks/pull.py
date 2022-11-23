from biobricks import bblib, token
import os, urllib.request as request, dvc.api, pathlib

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

    bblib(org).mkdir(exist_ok=True)

    def psys(path): 
        return lambda cmd: os.system(f"cd {path}; {cmd}")
        
    psys(bblib())(f"git submodule add {url} {repo}")
    
    rsys = psys(bblib(repo))
    rsys("dvc cache dir ../../cache")
    rsys("dvc config cache.shared group")
    rsys("dvc config cache.type symlink")
    rsys(f"git commit -m \"added {repo}\"")

    # SET UP BIOBRICKS.AI DVC REMOTE WITH AUTH
    rsys("dvc remote add -f biobricks.ai https://dvc.biobricks.ai")
    rsys("dvc remote modify --local biobricks.ai auth custom")
    rsys("dvc remote modify --local biobricks.ai custom_auth_header BBToken")
    rsys(f"dvc remote modify --local biobricks.ai password {token()}")

    # TODO handle file types other than parquet
    fs = dvc.api.DVCFileSystem(bblib(repo))
    paths = fs.find("data",maxdepth=1) + fs.find("brick",maxdepth=1)
    parquet = [x for x in paths if x.endswith('.parquet')]

    for file in parquet:
        os.system(f"cd {bblib(repo)}; dvc pull {file}")
    
    return True