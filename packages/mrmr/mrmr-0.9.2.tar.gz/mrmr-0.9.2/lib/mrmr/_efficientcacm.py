
from __future__ import division, print_function

from itertools import chain
from operator import itemgetter

import multiprocessing as mp
import numpy as np

# from _mrmr._fakepool import FakePool


__all__ = ['FastCaim']


class BSTree(object):
    def __init__(self, k, v, l=None, r=None):
        if l is not None:
            assert isinstance(l, BSTree)
        if r is not None:
            assert isinstance(r, BSTree)

        self.k = k
        self.v = v
        self.l = l
        self.r = r

    def __len__(self):
        ll = 0 if self.l is None else len(self.l)
        rl = 0 if self.r is None else len(self.r)
        return 1 + ll + rl

    def height(self):
        lh = 0 if self.l is None else self.l.height()
        rh = 0 if self.r is None else self.r.height()
        return 1 + max(lh, rh)

    def keys(self):
        if self.l is not None:
            r = self.l.keys()
            r.append(self.k)
        else:
            r = [k]
        if self.r is not None:
            r.extend(self.r.keys())
        return r

    def values(self):
        if self.l is not None:
            r = self.l.values()
            r.append(self.v)
        else:
            r = [self.v]
        if self.r is not None:
            r.extend(self.r.values())
        return r

    def items(self):
        if self.l is not None:
            r = self.l.items()
            r.append((self.k, self.v))
        else:
            r = [(self.k, self.v)]
        if self.r is not None:
            r.extend(self.r.items())
        return r

    def insert(self, k, v):
        if k < self.k:
            if self.l is not None:
                self.l.insert(k, v)
            else:
                self.l = BSTree(k, v)
        elif k > self.k:
            if self.r is not None:
                self.r.insert(k, v)
            else:
                self.r = BSTree(k, v)
        else:
            self.k, self.v = k, v

    def leaves(self):
        if self.l is None and self.r is None:
            r = [(self.k, self.v)]
        else:
            if self.l is not None:
                r = self.l.leaves()
            else:
                r = None
            if self.r is not None:
                if r is None:
                    r = self.r.leaves()
                else:
                    r.extend(self.r.leaves())
        assert r is not None, "leaves() should always return a list"
        return r


def _split(xy, classes):
    nrow, = xy.shape
    assert nrow > 1, "cannot split an interval of 1"
    maxi, maxc = None, None
    wgca, wgcb = None, None
    for i in range(1, nrow-1):
        a = sum(np.sum(xy['class'][:i] == c) ** 2 for c in classes) / i
        b = sum(np.sum(xy['class'][i:] == c) ** 2 for c in classes) / (nrow - i)
        c = a + b - sum(np.sum(xy['class']     == c) ** 2 for c in classes) / nrow
        if maxi is None or maxc is None or c > maxc:
            maxi, maxc = i, c
            wgca, wgcb = i - a, nrow - i - b
    return maxi, maxc, wgca, wgcb


def _compute_cacm(x, y):
    assert(x.shape == y.shape)

    nrow, = y.shape

    dtype = [('value', float), ('class', int)]
    sortxy = np.zeros((nrow,), dtype=dtype)
    sortxy['value'] = x
    sortxy['class'] = y
    sortxy.sort(order='value')

    midpoints = (sortxy['value'][1:] + sortxy['value'][:-1]) / 2.
    classes = set(y)

    i, splitmax, wgca, wgcb = _split(xy, classes)
    maxcacm = splitmax / 2
    bounds = BSTree(midpoints[i-1], (((0, i), wgca), ((i, nrow-1), wgcb)))
    k = 2
    while True:
        interval, maxw = None, None
        for _, v in bounds.leaves()
            for ival, w in v:
                if maxw is None or w > maxw:
                    interval, maxw = ival, w
        j, k = interval
        i, splitmax, wgca, wgcb = _split(xy[j:k], classes)
        i += j
        cacm = # some recursive bullshit I don't get yet
        if k < len(classes) and cacm > maxcacm:
            maxcacm = cacm
            bounds.insert(midpoints[i-1], (((j, i), wgca), ((i, k), wgcb)))
        else:
            break
    return maxcacm, [k for k, _ in bounds.leaves()]


def _discretize(x, b):
    n = np.zeros(x.shape, dtype=int)
    for i in range(b.shape[0]):
        n += (x > b[i])
    return n


class EfficientCacm(object):
    '''
    Implements the Efficient CACM algorithm from the paper 
    An effective discretization based on Class-Attribute Coherence Maximization
    by Min Li, ShaoBo Deng, Shengzhong Feng, Jianping Fan
    '''

    def __init__(self):
        self.__boundaries = None

    def learn(self, x, y):
        self.__boundaries = None

        np_err = np.seterr(divide='ignore')

        nrow, ncol = x.shape
        self.__x = np.array(x.T, dtype=float, copy=True)
        self.__y = np.array(y, dtype=np.int32, copy=True).reshape(nrow)

        if mp.current_process().daemon:
            from _fakepool import FakePool
            pool = FakePool()
        else:
            pool = mp.Pool(mp.cpu_count())

        res = []

        for j in range(ncol):
            res.append(pool.apply_async(_compute_cacm, (self.__x[j, :], self.__y)))

#         newx = np.zeros(self.__x.shape, dtype=int)
        caims = np.zeros((ncol,), dtype=float)
        boundaries = []

        pool.close()
        pool.join()

        for j in range(ncol):
            caims[j], b = res[j].get()
            boundaries.append(b)

        np.seterr(**np_err)

        self.__boundaries = boundaries

    def discretize(self, x):
        if self.__boundaries is None:
            raise RuntimeError("An Efficient-CACM model hasn't been learned.")

        if x.shape[1] != len(self.__boundaries):
            raise ValueError("x is incompatible with learned model: differing numbers of columns")

        newx = np.zeros(x.shape, dtype=int)

        for i in range(newx.shape[1]):
            b = self.__boundaries[i]
            for j in range(b.shape[0]):
                newx[:, i] += (x[:, i] > b[j])

#         pool = mp.Pool(mp.cpu_count())
#
#         res = []
#
#         # I don't usher everything around in result objects because
#         # these columns are accessed independently of one another ... I hope
#         for i in xrange(newx.shape[1]):
#             res.append(pool.apply_async(_discretize, (x[:, i], self.__boundaries[i])))
#
#         pool.close()
#         pool.join()
#
#         for i in xrange(newx.shape[1]):
#             newx[:, i] = res[i].get()

        return newx
