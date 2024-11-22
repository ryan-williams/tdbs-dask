# tdbs-dask
Experiments reading TileDB-SOMA data using Dask.

- [TileDBSOMA@rw/ad-dask] supports exporting `Experiment`s and `ExperimentAxisQuery`s to AnnData with Dask-Array X 
- WIP code in this repo transpiles Dask DAGs to TileDB UDFs, e.g.:
  - [Random array + elementwise multiplication](tests/test_transpile_dask.py#L22)
  - [TDBS-Dask pbmc-small dataset](tests/test_transpile_dask.py#L54)

## Install <a id="install"></a>
```bash
git clone https://github.com/ryan-williams/tdbs-dask && cd tdbs-dask 
pip install -e .
```

## Appendix <a id="appendix"></a>
Extends work by [**@ivirshup**]:
- [access_tiledb_w_dask.ipynb]
- [map-blocks-approach-ipynb]
- [write-tiledb-from-dask.ipynb]


[TileDBSOMA@rw/ad-dask]: https://github.com/single-cell-data/TileDB-SOMA/compare/main...rw/ad-dask
[**@ivirshup**]: https://github.com/ivirshup
[access_tiledb_w_dask.ipynb]: https://gist.github.com/ivirshup/8500d9a874ea9313ca87c0d5e46886e9
[map-blocks-approach-ipynb]: https://gist.github.com/ivirshup/dc39029ad439cef4755e45582fc35541#file-map-blocks-approach-ipynb
[write-tiledb-from-dask.ipynb]: https://gist.github.com/ivirshup/018bb8ae1ea7746db768c3672b8a007b
[Dask]: https://dask.org/
[CELLxGENE Census]: https://chanzuckerberg.github.io/cellxgene-census/
[Anndata]: https://anndata.readthedocs.io/en/latest/
