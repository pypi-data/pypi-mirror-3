if __name__ == '__main__':
    from prody import *
    from time import time
    select.DEBUG=1
    p = parsePDB('1aar')
    t = time()
    print '|#>', repr(p.select('beta >= beta + 0 ** 2 ^ 2 * 1 / 1 > occupancy > 0'), )
    print time()-t
    t = time()
    print '|#>', repr(p.select('beta > 0 and protein'), )
    print time()-t

