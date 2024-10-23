import pytest

from tiledbsoma_dask.cli.outgest_census import load_daskarray, CENSUS_S3


@pytest.mark.parametrize("use_tiledbsoma", [True, False])
def test_census_dask_array_read(use_tiledbsoma):
    exp_uri = f"{CENSUS_S3}/2024-07-01/soma/census_data/homo_sapiens"
    uri = f"{exp_uri}/ms/RNA/X/raw/"
    X = load_daskarray(
        uri=exp_uri if use_tiledbsoma else uri,
        chunk_size=1_000,
        nrows=4_000,
        use_tiledbsoma=use_tiledbsoma,
        measurement_name="RNA",
        X_layer_name="raw",
    )
    X = X.compute()
    assert X.shape == (4_000, 60_530)
    assert X.nnz == 2_692_562
