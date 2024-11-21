from typing import Any, Tuple

from click import command

import dask.array as da
from dask.optimization import SubgraphCallable


class Graph:
    def __init__(self, dask):
        self.dask = dask
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

    def eval(self, k: str | Tuple[str, int, ...]) -> Any:
        if k not in self.dask:
            raise KeyError(f"{k} not found in {', '.join(self.dask.keys())}")
        if k not in self._evals:
            v = self.dask[k]
            fn, *args = v
            if isinstance(fn, SubgraphCallable):
                args2 = []
                for arg in args:
                    if isinstance(arg, tuple) and isinstance(arg[0], str):
                        evald = self.eval(arg)
                        args2.append(evald)
                    else:
                        args2.append(arg)
                self._evals[k] = fn(*args2)
            else:
                self._evals[k] = fn(*args)

        return self._evals[k]


def transpile_dask(darr: da.Array):
    dsk = darr.dask
    root_layers = [ k for k, v in dsk.dependents.items() if not v ]
    if len(root_layers) != 1:
        raise ValueError(f"Expected 1 root layer, found {len(root_layers)}: {root_layers}")
    [root_layer] = root_layers
    leaf_layers = [ k for k, v in dsk.dependencies.items() if not v ]
    return root_layer, leaf_layers


@command
def main():
    pass


if __name__ == '__main__':
    main()
