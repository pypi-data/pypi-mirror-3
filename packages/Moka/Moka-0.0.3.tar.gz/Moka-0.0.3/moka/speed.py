def test():
    import __init__ as moka
    import string
    x = moka.List(['a']).map(string.zfill, 3)


def test2():
    import __init__ as moka
    import string
    x = [string.zfill(x, 3) for x in ['a']]

if __name__ == '__main__':
    time = 100000
    from timeit import Timer
    print Timer("test()", "from __main__ import test").timeit(time)
    print Timer("test2()", "from __main__ import test2").timeit(time)
