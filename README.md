# BioBricks
<!-- badges: start -->
[![codecov](https://codecov.io/gh/biobricks-ai/biobricks/branch/master/graph/badge.svg?token=J041MF0JKG)](https://codecov.io/gh/biobricks-ai/biobricks-r)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
<!-- badges: end -->

BioBricks is a tool to load data from biological datasets in an easy and
automated way.

## Installation

To install BioBricks package use the python packagge manager `pip`.

```bash
$ pip install biobricks
```

## Usage

To import BioBricks package use the following state:

```python
import biobricks as bb
```

The first time you use BioBricks package, an initialization is required with the following process. 
1.  Set an environment variable `BBLIB` in your shell with the desired location path of BioBricks library. Be sure you have enough available space to save locally your bricks. 

```shell
export BBLIB=/opt/biobricks
echo $BBLIB
```

2.  Obtain a BioBricks account from the following link: https://members.biobricks.ai/register. Go to your email an validate your account. Once you succefully login to BioBricks website go to the link https://members.biobricks.ai/token to obtain a token. Copy your token and use it in the following statement:

```python
bb.initialize(<YOUR TOKEN>)
```

To download a brick and save it locally in your library use the function `bb.pull`. As an example, Tox21 data dataset can be downlaoded with the following statement.  

```python
bb.pull('tox21')
```

Once the dataset is stored locally in the BioBricks library, the data can be loaded with `bb.load` function.

```python
tox21 = bb.load('tox21')
```

This function returns a `SimpleNamespace` object with all the tables available in the dataset. The tables are store in `pyarrow.Table` type. To list the available table the in the `SimpleNamespace` object use:

```python
tablenames = sorted(list(vars(tox21).keys()))
for tablename in tablenames:
    print(tablename)
```

The list of avaible tables can be visulized with the autocomplete functionality in your python editor.

To convert a pyarrow table to a pandas data frame use the following statement:

```python
ache_p4 = tox21.tox21_ache_p4.to_pandas()
```

To list the bricks currently available in the BioBricks GitHub
repository you can visit:

https://github.com/biobricks-ai

## Complete example

```python
import biobricks as bb

bb.pull('tox21')
tox21 = bb.load('tox21')
tablenames = sorted(list(vars(tox21).keys()))
for tablename in tablenames:
    print(tablename)
ache_p4 = tox21.tox21_ache_p4.to_pandas()
print(ache_p4.head())
```