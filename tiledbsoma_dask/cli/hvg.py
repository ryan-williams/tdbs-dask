from typing import Literal

import anndata as ad
import scanpy as sc
from click import option

from .base import cli
from ..utils import DEFAULT_MEASUREMENT, DEFAULT_X_LAYER, load_daskarray

CENSUS_S3 = "s3://cellxgene-census-public-us-west-2/cell-census"
DEFAULT_CENSUS_VERSION = "2024-07-01"

DEFAULT_CHUNK_SIZE = 1e4
DEFAULT_NROWS = 1e6

Species = Literal["homo_sapiens", "mus_musculus"]


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
