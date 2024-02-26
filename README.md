# BioBricks
<!-- badges: start -->
[![codecov](https://codecov.io/gh/biobricks-ai/biobricks/branch/master/graph/badge.svg?token=J041MF0JKG)](https://codecov.io/gh/biobricks-ai/biobricks)
<!-- badges: end -->

BioBricks makes loading data from biological datasets easy.

```bash
pipx install biobricks
```

# initialize
To get started configure biobricks with a path for bricks and a biobricks.ai token:
```
biobricks configure
> Choose path to store bricks: <input a local path>
> Input a token from biobricks.ai/token: <this is your access token>
```

# Install and Use Bricks

To install a brick the command line command:
```sh
> biobricks install tox21
```

You can then use the brick in python as below:
```python
import biobricks as bb
bb.assets('tox21') # get the paths for the 'tox21' brick
```

To list the bricks currently available visit [status.biobricks.ai](https://status.biobricks.ai)
