from tiledbsoma_dask.cli.hvg import load_daskarray, CENSUS_S3


def test_census_dask_array_read():
    uri = f"{CENSUS_S3}/2024-07-01/soma/census_data/homo_sapiens"
    X = load_daskarray(
        uri=uri,
        chunk_size=1_000,
        nrows=4_000,
        measurement_name="RNA",
        X_layer_name="raw",
    )
    X = X.compute()
    assert X.shape == (4_000, 60_530)
    assert X.nnz == 2_692_562
