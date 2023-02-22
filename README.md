# BioBricks
<!-- badges: start -->
[![codecov](https://codecov.io/gh/biobricks-ai/biobricks/branch/master/graph/badge.svg?token=J041MF0JKG)](https://codecov.io/gh/biobricks-ai/biobricks-r)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
<!-- badges: end -->

BioBricks makes loading data from biological datasets easy.

```bash
pip install biobricks
```

# initialize
To initialize BioBricks you must set the `BBLIB` environmental variable and get a user token.
1. **`TOKEN`:** register at [biobricks.ai](https://biobricks.ai/register) then go to [biobricks.ai/token](https://biobricks.ai/token)
2. **`BBLIB`:** Set this to a path on your local file system with plenty of space for large bricks

```python
import biobricks as bb
os.environ['BBLIB'] = '/some/path' # typically set this up to persist between python sessions
bb.initialize(<TOKEN>) # see step 1 above
```

# Pull Bricks
To download a brick and save it locally in your library use `bb.pull`. An example using the Tox21 dataset:  

```python
bb.pull('tox21') # save the brick to BBLIB and download it's resources
tox21 = bb.load('tox21') # load a SimpleNamespace with all the brick tables

# List the resources in the brick
for tablename in sorted(list(vars(tox21).keys())):
    print(tablename)
    
tox21.tox21_ache_p4.to_pandas() # get a pyarrow Table and convert to pandas dataframe
```

To list the bricks currently available visit [github.com/biobricks-ai](https://github.com/biobricks-ai)

# How does this all work?

Installing biobricks creates a BBLIB directory with a .cache subdirectory and many commit hashes representing bricks. The .cache directory is managed by dvc and stores the brick assets that are symlinked in bricks. The commit hashes are git repos referenced by their sha. The structure looks like this:

```
BBLIB/
    .cache/ # managed by dvc, stores brick assets symlinked in bricks
    74aed53360e5a278931b2f8eac0702f28fd444e4/ # a git repo 
    0aeb15ffa06be6c43ec5b654f6a8ff6ea4fa2bef/ # a git repo 
    ...
```

When writing code it is desirable to load brick assets by repository names, org/repo syntax, or by commit hash. For example, to load biobricks tox21 you could use:

```python
import biobricks as bb

# Load the 'latest' version of the brick
tox21 = bb.load("tox21") 
tox21 = bb.load("biobricks-ai/tox21")

# Load a specific version
tox21 = bb.load("biobricks-ai/tox21/74aed53360e5a278931b2f8eac0702f28fd444e4")
tox21 = bb.load("https://github.com/biobricks-ai/tox21#74aed53360e5a278931b2f8eac0702f28fd444e4")
```