from typing import Any, Tuple, Callable, Sequence, Union

import numpy as np
from click import command
from tiledb.cloud.compute import Delayed

import dask.array as da
from dask.array.core import finalize
from dask.optimization import SubgraphCallable


class Graph:
    def __init__(self, darr: da.Array):
        self.darr = darr
        self.dask = darr.dask
        self._evals = {}

    @property
    def root_layer(self) -> str:
        root_layers = [ k for k, v in self.dask.dependents.items() if not v ]
        if len(root_layers) != 1:
            raise ValueError(f"Expected 1 root layer, found {len(root_layers)}: {root_layers}")
        [root_layer] = root_layers
        return root_layer

    @property
    def leaf_layers(self) -> list[str]:
        return [ k for k, v in self.dask.dependencies.items() if not v ]

    def __dict__(self):
        return dict(self.dask)

    def __iter__(self):
        return iter(self.dask)

    @property
    def nodes(self):
        return list(self.dask.items())

    def compute(self, local: bool = True):
        evald = { k: self.eval(k, local=local) for k in self }
        root_layer = self.root_layer
        results = {}
        def save(results, idxs, block):
            idx, *rest = idxs
            if not rest:
                results[idx] = block
            else:
                if idx not in results:
                    results[idx] = {}
                save(results[idx], rest, block)

        for (layer, *idxs), block in evald.items():
            if layer != root_layer:
                continue
            save(results, idxs, block)

        def to_tpls(results):
            if isinstance(results, dict):
                idxs = list(range(len(results)))
                assert list(results.keys()) == idxs
                return tuple(to_tpls(results[idx]) for idx in idxs)
            else:
                return results

        results_tpl = to_tpls(results)
        return finalize(results_tpl)

    def call(self, fn: Callable, args: Sequence, local: bool = True) -> Any:
        tile_fn = Delayed(fn, local=local)
        res = tile_fn(*args).compute()
        return res

    def eval(self, k: Union[str, Tuple], local: bool = True) -> Any:
        if k not in self.dask:
            raise KeyError(f"{k} not found in {', '.join(self.dask.keys())}")
        if k not in self._evals:
            v = self.dask[k]
            if isinstance(v, (np.ndarray, dict)):
                self._evals[k] = v
            elif isinstance(v, tuple):
                fn, *args = v
                if isinstance(fn, SubgraphCallable):
                    dsk = fn.dsk
                    args2 = []
                    for arg in args:
                        if isinstance(arg, tuple) and isinstance(arg[0], str):
                            evald = self.eval(arg, local=local)
                            args2.append(evald)
                        else:
                            args2.append(arg)
                    [ (sub_fn, *sub_args) ] = list(dsk.values())
                    inkeys_map = { k: i for i, k in enumerate(fn.inkeys) }
                    def normalize(arg):
                        if isinstance(arg, list):
                            return [ normalize(a) for a in arg ]
                        elif isinstance(arg, str):
                            if arg in inkeys_map:
                                return normalize(args[inkeys_map[arg]])
                            elif arg in self.dask:
                                return self.eval(arg, local=local)
                            else:
                                return arg
                        elif isinstance(arg, tuple):
                            if isinstance(arg[0], str):
                                return self.eval(arg, local=local)
                            elif arg[0] is dict:
                                return { k: normalize(v) for k, v in arg[1] }
                            elif arg[0] is tuple:
                                return tuple(arg[1])
                            else:
                                return arg
                        else:
                            return arg

                    sub_args2 = [ normalize(arg) for arg in sub_args ]
                    sub_val = self.call(sub_fn, sub_args2, local=local)
                    self._evals[k] = sub_val
                else:
                    self._evals[k] = self.call(fn, args, local=local)
            else:
                raise ValueError(f"Dask key {k}: unrecognized value type {type(v)}: {v}")

        return self._evals[k]


@command
def main():
    pass


if __name__ == '__main__':
    main()
