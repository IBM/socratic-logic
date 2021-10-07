import time


def clock(fn, *args, **kwargs):
    t = time.time()

    try:
        ret = fn(*args, **kwargs)

    finally:
        t = time.time() - t

        print('fn:  ', fn.__name__, args, kwargs)
        print('time:', t)

    return ret
