from typing import Literal

import anndata as ad
import dask.array as da
import scanpy as sc
import tiledb
from click import option
from scipy import sparse

from .base import cli
from ..utils import to_listed_chunks

CENSUS_S3 = "s3://cellxgene-census-public-us-west-2/cell-census"
DEFAULT_CENSUS_VERSION = "2024-07-01"

DEFAULT_CHUNK_SIZE = 1e4
DEFAULT_NROWS = 1e6
DEFAULT_MEASUREMENT = "RNA"
DEFAULT_X_LAYER = "raw"

CTX = {
    "vfs.s3.no_sign_request": "true",
    "vfs.s3.region": "us-west-2"
}

Species = Literal["homo_sapiens", "mus_musculus"]


def sparse_chunk(
    block_id,
    block_info,
    uri: str,
):
    shape = block_info[None]["chunk-shape"]
    array_location = block_info[None]["array-location"]
    (obs_start, obs_end), (var_start, var_end) = array_location
    obs_slice = slice(obs_start, obs_end)
    var_slice = slice(var_start, var_end)
    ctx = tiledb.Ctx(CTX)
    with tiledb.open(uri, ctx=ctx) as tiledb_array:
        block = tiledb_array[obs_slice, var_slice]
    soma_dim_0, soma_dim_1, count = block["soma_dim_0"], block["soma_dim_1"], block["soma_data"]
    soma_dim_0 -= obs_start
    soma_dim_1 -= var_start
    return sparse.csr_matrix((count, (soma_dim_0, soma_dim_1)), shape=shape)


def load_daskarray(
    uri: str,
    chunk_size: int,
    nrows: int,
):
    """Load a TileDB-SOMA X layer as a Dask array, using ``tiledb`` or ``tiledbsoma``."""
    with tiledb.open(uri, config=CTX) as tiledb_array:
        dtype = tiledb_array.dtype
        nvars = tiledb_array.shape[1]

    X = da.map_blocks(
        sparse_chunk,
        chunks=(
            tuple(to_listed_chunks(chunk_size, nrows)),
            (nvars,)
        ),
        meta=sparse.csr_matrix((0, 0), dtype=dtype),
        uri=uri,
    )
    return X


def hvg(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    measurement_name: str = DEFAULT_MEASUREMENT,
    mus_musculus: bool = False,
    nrows: int = DEFAULT_NROWS,
    census_version: str = DEFAULT_CENSUS_VERSION,
    X_layer_name: str = DEFAULT_X_LAYER,
):
    """Compute highly-variable genes on a subset of CELLxGENE Census data, reading TileDB-SOMA data using Dask."""
    species: Species = "mus_musculus" if mus_musculus else "homo_sapiens"
    uri = f"{CENSUS_S3}/{census_version}/soma/census_data/{species}/ms/{measurement_name}/X/{X_layer_name}"
    X = load_daskarray(
        uri=uri,
        chunk_size=chunk_size,
        nrows=nrows,
    )

    adata = ad.AnnData(X=X)
    sc.pp.normalize_total(adata)
    sc.pp.log1p(adata)
    return sc.pp.highly_variable_genes(adata, inplace=False, subset=True)


@cli.command('hvg')
@option('-c', '--chunk-size', type=int, default=DEFAULT_CHUNK_SIZE)
@option('-m', '--mus-musculus', is_flag=True, help="Query Census for mouse data (default: human)")
@option('-M', '--measurement-name', default=DEFAULT_MEASUREMENT, help=f'Experiment "measurement" to read (default: "{DEFAULT_MEASUREMENT}")')
@option('-n', '--nrows', type=int, default=DEFAULT_NROWS)
@option('-v', '--census-version', default=DEFAULT_CENSUS_VERSION, help="")
@option('-X', '--X-layer-name', 'X_layer_name', default=DEFAULT_X_LAYER, help=f'"X" layer to read (default: "{DEFAULT_X_LAYER}")')
def hvg_cmd(*args, **kwargs):
    df = hvg(*args, **kwargs)
    print(df)
