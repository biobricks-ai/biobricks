from biobricks import bblib
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
    os.system(f"cd {bblib()}; git submodule add {url} {repo}")
    os.system(f"cd {bblib(repo)}; dvc cache dir ../../cache")
    os.system(f"cd {bblib(repo)}; dvc config cache.shared group")
    os.system(f"cd {bblib(repo)}; dvc config cache.type symlink")
    os.system(f"cd {bblib()}; git commit -m \"added {repo}\"")

    # TODO handle file types other than parquet
    fs = dvc.api.DVCFileSystem(bblib(repo))
    paths = fs.find("data",maxdepth=1) + fs.find("brick",maxdepth=1)
    parquet = [x for x in paths if x.endswith('.parquet')]

    for file in parquet:
        os.system(f"cd {bblib(repo)}; dvc pull {file}")
    
    return True