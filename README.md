# tdbs-dask
Experiments reading TileDB-SOMA data using Dask.

Extends work by [**@ivirshup**]:
- [access_tiledb_w_dask.ipynb]
- [map-blocks-approach-ipynb]
- [write-tiledb-from-dask.ipynb]

Currently one CLI command, for converting a subset of CELLxGENE Census to a Dask-backed Anndata, then running Scanpy highly-variable genes on it:

```bash
git clone https://github.com/ryan-williams/tdbs-dask && cd tdbs-dask 
pip install -e .
```

<!-- `bmdf -- tdbs-dask hvg --help` -->
```bash
tdbs-dask hvg --help
# Usage: tdbs-dask hvg [OPTIONS]
#
#   Compute highly-variable genes on a subset of CELLxGENE Census data, reading
#   TileDB-SOMA data using Dask.
#
# Options:
#   -c, --chunk-size INTEGER
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


[**@ivirshup**]: https://github.com/ivirshup
[access_tiledb_w_dask.ipynb]: https://gist.github.com/ivirshup/8500d9a874ea9313ca87c0d5e46886e9
[map-blocks-approach-ipynb]: https://gist.github.com/ivirshup/dc39029ad439cef4755e45582fc35541#file-map-blocks-approach-ipynb
[write-tiledb-from-dask.ipynb]: https://gist.github.com/ivirshup/018bb8ae1ea7746db768c3672b8a007b
