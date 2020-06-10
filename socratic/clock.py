import time


def clock(fn, *args, **kwargs):
    t = time.time()

    ret = fn(*args, **kwargs)

    t = time.time() - t

    print('fn:  ', fn.__name__, args, kwargs)
    print('time:', t)

    return ret
