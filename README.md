# tdbs-dask
Experiments reading TileDB-SOMA data using Dask.

<!-- toc -->
- [Install](#install)
- [CLI](#cli)
- [Examples](#examples)
    - [100x10,000 chunks, using `tiledbsoma`](#tiledbsoma-1e6)
    - [100x10,000 chunks, using `tiledb`](#tiledb-1e6)
<!-- /toc -->

Extends work by [**@ivirshup**]:
- [access_tiledb_w_dask.ipynb]
- [map-blocks-approach-ipynb]
- [write-tiledb-from-dask.ipynb]

## Install <a id="install"></a>
```bash
git clone https://github.com/ryan-williams/tdbs-dask && cd tdbs-dask 
pip install -e .
```

## CLI <a id="cli"></a>
Currently one CLI command, `tdbs-dask hvg`, for converting a subset of [CELLxGENE Census] to [Anndata] (optionally [Dask]-backed), then running Scanpy highly-variable genes on it:

<!-- `bmdf -- tdbs-dask hvg --help` -->
```bash
tdbs-dask hvg --help
# Usage: tdbs-dask hvg [OPTIONS]
#
#   Compute highly-variable genes on a subset of CELLxGENE Census data, reading
#   TileDB-SOMA data using Dask.
#
# Options:
#   -c, --chunk-size INTEGER     Number of rows to process in each Dask task; 0
#                                to run without Dask (default: 10000.0
#   -m, --mus-musculus           Query Census for mouse data (default: human)
#   -M, --measurement-name TEXT  Experiment "measurement" to read (default:
#                                "RNA")
#   -n, --nrows INTEGER
#   -S, --no-tiledbsoma          Load `X` array chunks using `tiledb` instead of
#                                `tiledbsoma`
#   -v, --census-version TEXT
#   -X, --X-layer-name TEXT      "X" layer to read (default: "raw")
#   --help                       Show this message and exit.
```

## Examples <a id="examples"></a>

### 100x10,000 chunks, using `tiledbsoma` <a id="tiledbsoma-1e6"></a>
<!-- `bmdf -- time tdbs-dask hvg` -->
```bash
time -p tdbs-dask hvg
#           means  dispersions  ... dispersions_norm  highly_variable
# 0      0.048454     0.735610  ...         0.552318             True
# 4      0.031885     0.759286  ...         0.580610             True
# 5      0.094259     0.976116  ...         0.839716             True
# 6      0.209642     1.557129  ...         1.534013             True
# 8      0.090585     0.703962  ...         0.514499             True
# ...         ...          ...  ...              ...              ...
# 59770  0.031929     0.872826  ...         0.716287             True
# 59913  0.058735     1.416697  ...         1.366200             True
# 60199  0.054201     1.452568  ...         1.409066             True
# 60319  0.013607     1.169472  ...         1.070772             True
# 60415  0.023608     0.813904  ...         0.645877             True
#
# [8721 rows x 5 columns]
# real 210.91
# user 328.07
# sys 346.74
```

### 100x10,000 chunks, using `tiledb` <a id="tiledb-1e6"></a>
<!-- `bmdf -- time tdbs-dask hvg -S` -->
```bash
time -p tdbs-dask hvg -S
#           means  dispersions  ... dispersions_norm  highly_variable
# 0      0.048454     0.735610  ...         0.552318             True
# 4      0.031885     0.759286  ...         0.580610             True
# 5      0.094259     0.976116  ...         0.839716             True
# 6      0.209642     1.557129  ...         1.534013             True
# 8      0.090585     0.703962  ...         0.514499             True
# ...         ...          ...  ...              ...              ...
# 59770  0.031929     0.872826  ...         0.716287             True
# 59913  0.058735     1.416697  ...         1.366200             True
# 60199  0.054201     1.452568  ...         1.409066             True
# 60319  0.013607     1.169472  ...         1.070772             True
# 60415  0.023608     0.813904  ...         0.645877             True
#
# [8721 rows x 5 columns]
# real 90.66
# user 334.99
# sys 331.08
```


[**@ivirshup**]: https://github.com/ivirshup
[access_tiledb_w_dask.ipynb]: https://gist.github.com/ivirshup/8500d9a874ea9313ca87c0d5e46886e9
[map-blocks-approach-ipynb]: https://gist.github.com/ivirshup/dc39029ad439cef4755e45582fc35541#file-map-blocks-approach-ipynb
[write-tiledb-from-dask.ipynb]: https://gist.github.com/ivirshup/018bb8ae1ea7746db768c3672b8a007b
[Dask]: https://dask.org/
[CELLxGENE Census]: https://chanzuckerberg.github.io/cellxgene-census/
[Anndata]: https://anndata.readthedocs.io/en/latest/
