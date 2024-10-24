from typing import Optional

import dask.array as da
import tiledb
import tiledbsoma
from scipy import sparse
from somacore import AxisQuery
from tiledbsoma import SOMATileDBContext


DEFAULT_MEASUREMENT = "RNA"
DEFAULT_X_LAYER = "raw"
DEFAULT_CONFIG = {
    "vfs.s3.no_sign_request": "true",
    "vfs.s3.region": "us-west-2"
}


def to_listed_chunks(chunk_size: int, dim_size: int) -> list[int]:
    """Go from single integer to list representation of a chunking scheme.

    Some rules about how this behaves:

        d, r := divmod(n, mod)
        (*((mod,) * d), r) := to_listed_chunks(mod, n)
        map(len, itertools.batched(range(n), mod))) := to_listed_chunks(mod, n)


    Examples
    --------
    >>> to_listed_chunks(10, 25)
    [10, 10, 5]
    >>> to_listed_chunks(3, 9)
    [3, 3, 3]
    """
    n_full, rem = divmod(dim_size, chunk_size)
    chunk_list = [chunk_size] * n_full
    if rem:
        chunk_list += [rem]
    return chunk_list


def sparse_chunk(
    block_id,
    block_info,
    uri: str,
    use_tiledbsoma: bool,
    measurement_name: str,
    X_layer_name: str,
    tiledb_config: dict,
):
    shape = block_info[None]["chunk-shape"]
    array_location = block_info[None]["array-location"]
    (obs_start, obs_end), (var_start, var_end) = array_location
    obs_slice = slice(obs_start, obs_end - (1 if use_tiledbsoma else 0))
    var_slice = slice(var_start, var_end - (1 if use_tiledbsoma else 0))
    if use_tiledbsoma:
        with tiledbsoma.open(uri, context=SOMATileDBContext(tiledb_config=tiledb_config)) as exp:
            with exp.axis_query(
                measurement_name=measurement_name,
                obs_query=AxisQuery(coords=(obs_slice,)),
                var_query=AxisQuery(coords=(var_slice,)),
            ) as query:
                X = query.X(X_layer_name)
                tbl = X.tables().concat()
        soma_dim_0, soma_dim_1, count = [ col.to_numpy() for col in tbl.columns ]
    else:
        with tiledb.open(uri, config=tiledb_config) as tiledb_array:
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
    tiledb_config: Optional[dict] = None,
    measurement_name: str = DEFAULT_MEASUREMENT,
    X_layer_name: str = DEFAULT_X_LAYER,
):
    """Load a TileDB-SOMA X layer as a Dask array, using ``tiledb`` or ``tiledbsoma``."""
    if tiledb_config is None:
        tiledb_config = DEFAULT_CONFIG
    layer_uri = f"{exp_uri}/ms/{measurement_name}/X/{X_layer_name}"
    uri = exp_uri if use_tiledbsoma else layer_uri
    if use_tiledbsoma:
        soma_ctx = SOMATileDBContext(tiledb_config=tiledb_config)
        with tiledbsoma.open(uri, context=soma_ctx) as exp:
            X = exp.ms[measurement_name].X
            layer = X[X_layer_name]
            _, _, data_dtype = layer.schema.types
            dtype = data_dtype.to_pandas_dtype()
            nvars = layer.shape[1]
    else:
        with tiledb.open(uri, config=tiledb_config) as tiledb_array:
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
        tiledb_config=tiledb_config,
    )
    return X

