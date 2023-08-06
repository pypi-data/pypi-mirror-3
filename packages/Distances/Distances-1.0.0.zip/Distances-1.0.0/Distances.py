"""
    Distances 1.0.0
    ***************
    Simple distance algorithms for similarity
    zinark (ceferhat@gmail.com)
    http://www.blessedcode.net
"""
def pearson (x,y):
    """Returns pearson algorithm distance between same length two list """
    assert isinstance(x, list), 'x should be list'
    assert isinstance(y, list), 'y should be list'
    print 'x ',x
    print 'y ',y

    n = len (x)
    print 'len(x) n = ' , n
    vals = range (n)

    ex = sum (float(x[i]) for i in vals)
    ey = sum (float(y[i]) for i in vals)
    print 'ex ', ex
    print 'ey ', ey

    exsq = sum (float(x[i]**2) for i in vals)
    eysq = sum (float(y[i]**2) for i in vals)
    print 'exsq ', exsq
    print 'eysq ', eysq

    exy = sum (float(x[i]*y[i]) for i in vals)
    print 'exy ', exy

    num = exy - ex * ey / n
    print 'num ', num

    den = ((exsq - pow (ex,2) / n) * (eysq - pow (ey,2) / n)) ** 0.5
    print 'den ', den

    print 'num = Exy - ExEy / N = ', exy, '-', ex, '.', ey, '/', n
    print 'den = (Ex2 - (Ex)2 / N) (Ey2 - (Ey)2 / N) = (', exsq, '-', ex**2, '/', n, ')(', eysq, '-', ey**2, '/', n, ')'
    if den == 0: return 0

    print num / den
    return num / den

def euclidean (x,y):
    """Returns euclidean algorithm distance between same length two list """
    assert isinstance(x, list), 'x should be list'
    assert isinstance(y, list), 'y should be list'

    if not len(x):
        return 0

    squared = [(x[i] - y[i])**2 for i in range(0, len(x))]
    total = sum(squared)
    return  1 / float(1 + total)
