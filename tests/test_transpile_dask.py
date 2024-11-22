from os.path import dirname, join
from re import fullmatch

import dask

import dask.array as da
from numpy.ma.testutils import assert_array_equal
from tiledbsoma import Experiment
from tiledbsoma.io import to_anndata

from tiledb_dask.main import Graph

sha = r'(?P<sha>[\da-f]{32})'

def test_transpile_array():
    chunk = 2
    x = da.random.random((chunk * 2, chunk * 2), chunks=(chunk, chunk))
    x = da.map_blocks(lambda x: x * 10, x)
    graph = Graph(x.dask)
    evald = { k: graph.eval(k) for k in graph }
    root_layer = graph.root_layer
    assert fullmatch(f'lambda-{sha}', root_layer)
    [leaf_layer] = graph.leaf_layers
    assert fullmatch(f'random_sample-{sha}', leaf_layer)
    for i in range(2):
        for j in range(2):
            root_arr = evald[(root_layer, i, j)]
            leaf_arr = evald[(leaf_layer, i, j)]
            assert root_arr.shape == (chunk, chunk)
            assert leaf_arr.shape == (chunk, chunk)
            assert_array_equal(root_arr, leaf_arr * 10)


TESTS_DIR = dirname(__file__)
ROOT_DIR = dirname(TESTS_DIR)
PBMC_PATH = join(ROOT_DIR, "pbmc-small")


def test_tdbs_dask():
    exp = Experiment.open(PBMC_PATH)
    dask.config.set(scheduler="synchronous")
    add = to_anndata(exp, "RNA", dask_chunk_size=20)
    # x = add.X.compute()
    graph = Graph(add.X)
    evald = { k: graph.eval(k) for k in graph }
    assert len(evald) == 13
    # nodes = graph.nodes
    # assert len(nodes) == 12
