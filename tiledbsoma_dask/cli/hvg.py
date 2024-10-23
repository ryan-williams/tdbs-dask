from typing import Literal

import anndata as ad
import dask.array as da
import scanpy as sc
import tiledbsoma
import tiledb  # Must come after tiledbsoma! https://github.com/single-cell-data/TileDB-SOMA/issues/2293
from click import option
from scipy import sparse
from somacore import AxisQuery
from tiledbsoma import SOMATileDBContext

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
    use_tiledbsoma: bool,
    measurement_name: str,
    X_layer_name: str,
):
    shape = block_info[None]["chunk-shape"]
    array_location = block_info[None]["array-location"]
    (obs_start, obs_end), (var_start, var_end) = array_location
    obs_slice = slice(obs_start, obs_end - (1 if use_tiledbsoma else 0))
    var_slice = slice(var_start, var_end - (1 if use_tiledbsoma else 0))
    ctx = tiledb.Ctx(CTX)
    if use_tiledbsoma:
        with tiledbsoma.open(uri, context=SOMATileDBContext(ctx)) as exp:
            with exp.axis_query(
                measurement_name=measurement_name,
                obs_query=AxisQuery(coords=(obs_slice,)),
                var_query=AxisQuery(coords=(var_slice,)),
            ) as query:
                X = query.X(X_layer_name)
                tbl = X.tables().concat()
        soma_dim_0, soma_dim_1, count = [ col.to_numpy() for col in tbl.columns ]
    else:
        with tiledb.open(uri, ctx=ctx) as tiledb_array:
            block = tiledb_array[obs_slice, var_slice]
        soma_dim_0, soma_dim_1, count = block["soma_dim_0"], block["soma_dim_1"], block["soma_data"]
    soma_dim_0 = soma_dim_0 - obs_start
    soma_dim_1 = soma_dim_1 - var_start
    return sparse.csr_matrix((count, (soma_dim_0, soma_dim_1)), shape=shape)


def load_daskarray(
    exp_uri: str,
    chunk_size: int,
    nrows: int,
    use_tiledbsoma: bool,
    measurement_name: str = DEFAULT_MEASUREMENT,
    X_layer_name: str = DEFAULT_X_LAYER,
):
    """Load a TileDB-SOMA X layer as a Dask array, using ``tiledb`` or ``tiledbsoma``."""
    ctx = tiledb.Ctx(CTX)
    layer_uri = f"{exp_uri}/ms/{measurement_name}/X/{X_layer_name}"
    uri = exp_uri if use_tiledbsoma else layer_uri
    if use_tiledbsoma:
        soma_ctx = SOMATileDBContext(tiledb_ctx=ctx)
        with tiledbsoma.open(uri, context=soma_ctx) as exp:
            X = exp.ms[measurement_name].X
            layer = X[X_layer_name]
            _, _, data_dtype = layer.schema.types
            dtype = data_dtype.to_pandas_dtype()
            nvars = layer.shape[1]
    else:
        with tiledb.open(uri, ctx=ctx) as tiledb_array:
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
        measurement_name=measurement_name,
        X_layer_name=X_layer_name,
        use_tiledbsoma=use_tiledbsoma,
    )
    return X


def hvg(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    measurement_name: str = DEFAULT_MEASUREMENT,
    mus_musculus: bool = False,
    nrows: int = DEFAULT_NROWS,
    no_tiledbsoma: bool = False,
    census_version: str = DEFAULT_CENSUS_VERSION,
    X_layer_name: str = DEFAULT_X_LAYER,
):
    """Compute highly-variable genes on a subset of CELLxGENE Census data, reading TileDB-SOMA data using Dask."""
    species: Species = "mus_musculus" if mus_musculus else "homo_sapiens"
    soma_uri = f"{CENSUS_S3}/{census_version}/soma"
    exp_uri = f"{soma_uri}/census_data/{species}"
    use_tiledbsoma = not no_tiledbsoma
    X = load_daskarray(
        exp_uri=exp_uri,
        chunk_size=chunk_size,
        measurement_name=measurement_name,
        nrows=nrows,
        use_tiledbsoma=use_tiledbsoma,
        X_layer_name=X_layer_name,
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
@option('-S', '--no-tiledbsoma', is_flag=True, help='Load `X` array chunks using `tiledb` instead of `tiledbsoma`')
@option('-v', '--census-version', default=DEFAULT_CENSUS_VERSION, help="")
@option('-X', '--X-layer-name', 'X_layer_name', default=DEFAULT_X_LAYER, help=f'"X" layer to read (default: "{DEFAULT_X_LAYER}")')
def hvg_cmd(*args, **kwargs):
    df = hvg(*args, **kwargs)
    print(df)
