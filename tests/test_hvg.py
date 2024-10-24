import pytest

from tiledbsoma_dask.cli.hvg import CENSUS_S3, DEFAULT_CENSUS_VERSION
from tiledbsoma_dask.utils import load_daskarray


@pytest.mark.parametrize("use_tiledbsoma", [True, False])
def test_census_dask_array_read(use_tiledbsoma):
    exp_uri = f"{CENSUS_S3}/{DEFAULT_CENSUS_VERSION}/soma/census_data/homo_sapiens"
    X = load_daskarray(
        exp_uri=exp_uri,
        chunk_size=1_000,
        nrows=4_000,
        use_tiledbsoma=use_tiledbsoma,
        measurement_name="RNA",
        X_layer_name="raw",
    )
    X = X.compute()
    assert X.shape == (4_000, 60_530)
    assert X.nnz == 2_692_562
