import numpy as np
from numba import njit


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


@njit
def cmap(x, y, out=None):
    if out is None:
        out = np.empty_like(x)
    d = dict()
    for i, y_i in enumerate(y):
        d[y_i] = i
    # out = np.empty_like(y, shape=x.shape)
    for i, x_i in enumerate(x):
        out[i] = d[x_i]
    return out


def list_split(arr_list:list, sublist_len: int) -> list[list]:
    """Splits a python list into a list of sublists where each sublist is of size `sublist_len`.
    TODO: Replace with `itertools.batched` when Python 3.12 becomes the minimum supported version.
    """
    i = 0
    result = []

    while i < len(arr_list):
        if (i + sublist_len) >= len(arr_list):
            result.append(arr_list[i:])
        else:
            result.append(arr_list[i : i + sublist_len])

        i += sublist_len

    return result


