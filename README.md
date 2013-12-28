python-lzo-indexer
==================

![](https://travis-ci.org/duedil-ltd/python-lzo-indexer.png)

Python library for indexing block offsets within LZO compressed files. The implementation is largely based on that of the [Hadoop Library](https://github.com/twitter/hadoop-lzo). Index files are used to allow Hadoop to split a single file compressed with LZO into several chunks for parallel processing.

Since LZO is a block based compression algorithm, we can split the file along the lines of blocks and decompress each block on it's own. The index is a file containing byte offsets for each block in the original LZO file.


Example
-------

The python code below demonstrates how easy it is to index an LZO file. This library also supports indexing a string, and a method to return the individual block offsets should you need to create a file of your own format.

```python
import lzo_indexer

with open("my-file.lzo", "r") as f:
    with open("my-file.lzo.index", "rw") as index:
        lzo_indexer.index_lzo_file(f, index)
```


Command-line Utility
--------------------

This library also includes a utility for indexing multiple lzo files, using the python indexer. This is a much faster alternative to the command line utility built into the hadoop-lzo library as it avoids the JVM.

```
$ bin/lzo-indexer --help

usage: lzo-indexer [-h] [--verbose] [--force] lzo_files [lzo_files ...]

positional arguments:
  lzo_files      List of LZO files to index

optional arguments:
  -h, --help     show this help message and exit
  --verbose, -v  Enable verbose logging
  --force, -f    Force re-creation of an index even if it exsts
```


Contributions
-------------

I welcome any contributions, though I request that any pull requests come with test coverage.
