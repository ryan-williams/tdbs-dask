from tiledbsoma_dask.cli.hvg import load_daskarray, CENSUS_S3, DEFAULT_CENSUS_VERSION, DEFAULT_MEASUREMENT, \
    DEFAULT_X_LAYER


def test_census_dask_array_read():
    uri = f"{CENSUS_S3}/{DEFAULT_CENSUS_VERSION}/soma/census_data/homo_sapiens/ms/{DEFAULT_MEASUREMENT}/X/{DEFAULT_X_LAYER}"
    X = load_daskarray(
        uri=uri,
        chunk_size=1_000,
        nrows=4_000,
    )
    X = X.compute()
    assert X.shape == (4_000, 60_530)
    assert X.nnz == 2_692_562
