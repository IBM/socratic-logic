from time import time
from typing import Callable


def clock(fn: Callable, *args, **kwargs):
    """Print the running time of a function applied to the given arguments.

    Example usage:
        clock(time.sleep, 1)

    :param fn: The function to be clocked.
    :param args: Positional arguments for fn.
    :param kwargs: Labelled arguments for fn.
    :return: The return value of fn(*args, **kwargs).
    """
    t = time()

    try:
        ret = fn(*args, **kwargs)

    finally:
        t = time() - t

        print('fn:  ', fn.__name__, args, kwargs)
        print('time:', t)

    return ret
