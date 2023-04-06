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
To get started configure biobricks with a path for bricks and a biobricks.ai token:
```
biobricks configure
> Choose path to store bricks: <input a local path>
> Input a token from biobrick.ai/token: <this is your access token>
```

# Pull Bricks
To download a brick and save it locally in your library use `bb.pull`. An example using the Tox21 dataset:  

```python
import biobricks as bb
bb.install('tox21') # save the brick to the brick library and download it's resources
tox21 = bb.load('tox21') # load a SimpleNamespace with all the brick tables

# List the resources in the brick
for tablename in sorted(list(vars(tox21).keys())):
    print(tablename)
    
tox21.tox21_ache_p4.read().to_pandas() # get a pyarrow Table and convert to pandas dataframe
```

To list the bricks currently available visit [github.com/biobricks-ai](https://github.com/biobricks-ai)