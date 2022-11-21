from biobricks import bblib
import os, urllib, dvc.api

def pull(brick):
    repo = "biobricks-ai/"+brick
    url = "https://github.com/"+repo
    if urllib.request.urlopen(url).getcode()!=200:
        raise(Exception(f"{brick} not available in BioBricks"))
        
    repodir = bblib(repo)
    os.system(f"cd {repodir}; dvc cache dir ../../cache")
    os.system(f"cd {repodir}; dvc config cache.shared group")
    os.system(f"cd {repodir}; dvc config cache.type symlink")

    fs = dvc.api.DVCFileSystem(repodir)
    if(len(fs.find("brick")) > 0): os.system(f"cd {repodir}; dvc pull brick")
    if(len(fs.find("data")) > 0): os.system(f"cd {repodir}; dvc pull data")
    
    return True