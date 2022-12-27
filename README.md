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
1. **`TOKEN`:** register at [members.biobricks.ai](https://members.biobricks.ai/register) then go to [members.biobricks.ai/token](https://members.biobricks.ai/token)
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
