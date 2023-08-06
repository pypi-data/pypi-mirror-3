#
# idepi :: (IDentify EPItope) python libraries containing some useful machine
# learning interfaces for regression and discrete analysis (including
# cross-validation, grid-search, and maximum-relevance/mRMR feature selection)
# and utilities to help identify neutralizing antibody epitopes via machine
# learning.
#
# Copyright (C) 2011 N Lance Hepler <nlhepler@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import division, print_function

import numpy as np

try:
    from itertools import izip
except ImportError:
    izip = zip # py3 compatible

from multiprocessing import cpu_count

from fakemp import farmout, farmworker

from ._basemrmr import BaseMrmr
from ._discretemrmr import _compute_mi_inner as _discrete_compute_mi_inner


__all__ = ['DiscreteMrmr']



def _compute_mi_inner(classes_vars, tclasses, targets, nrow, Ncol, p=None):
    mi, h = [], []
    tcache = {}
    for vclass, vars in classes_vars:
        if vclass is not None:
            mi_v, h_v = _discrete_compute_mi_inner(vclass, vars, tclasses, targets)
            mi.append(mi_v)
            h.append(h_v)
        else:
            ncol = vars.shape[1]
            mi_v, h_v = np.zeros((ncol,), dtype=float), np.zeros((ncol,), dtype=float)
            for t in tclasses:
                if t in tcache:
                    nrow_given_t, targets_t = tcache[t]
                else:
                    targets_t = (targets == t).reshape((targets.size,))
                    nrow_given_t = np.sum(targets_t)
                    tcache[t] = (nrow_given_t, targets_t)
                for j in range(ncol):
                    # if bus errors happen here, upgrade to scipy 0.10.1 
                    p_v = DiffusionKde(vars[:, j].reshape((nrow,)))(vars[:, j].reshape((nrow,)))
                    # p(v, t) = p(v | t) * p(t), p(t)s cancel
                    vars_given_t = vars[np.where(targets_t), j].reshape((nrow_given_t,))
                    p_v_given_t = DiffusionKde(vars_given_t)(vars_given_t)
                    p_tv = p_v_given_t * (nrow_given_t / nrow)
                    mi_v[j] += np.nan_to_num(
                        np.multiply(
                            p_tv,
                            np.log2(p_v_given_t / p_v)
                        )
                    )
                    h_v[j] -= np.nan_to_num(np.multiply(p_tv, np.log2(p_tv)))
            pass

    if p is not None:
        p.value += 1

    return np.hstack(mi), np.hstack(h)


class DiscreteMrmr(BaseMrmr):

    def __init__(self, *args, **kwargs):
        super(DiscreteMrmr, self).__init__(*args, **kwargs)

    @staticmethod
    def _compute_mi(variables, targets, ui=None):

        targets = np.atleast_2d(targets)

        vrow, vcol = variables[0].shape[0], sum(subx.shape[1] for subx in variables)
        trow, tcol = targets.shape

        if trow == 1 and tcol == vrow:
            targets = targets.T
        elif tcol != 1 or trow != vrow:
            raise ValueError('`y\' should have as many entries as `x\' has rows.')

        vclasses = [set(vs.reshape(vs.size)) if np.issubdtype(vs.dtype, int) else None for vs in variables]
        tclasses = set(targets.reshape((targets.size,)))

        progress = None
        if ui:
            progress = ui.progress

#         numcpu = cpu_count()
#         percpu = int(vcol / numcpu + 0.5)

        return _compute_mi_inner(izip(vclasses, variables), tclasses, targets, vrow, vcol, progress)

#         results = farmout(
#             num=numcpu,
#             setup=lambda i: (
#                 _compute_mi_inner,
#                 nrow,
#                 vclasses, variables[:, (percpu*i):min(percpu*(i+1), ncol)],
#                 tclasses, targets,
#                 progress
#             ),
#             worker=farmworker,
#             isresult=lambda r: isinstance(r, tuple) and len(r) == 2,
#             attempts=1
#         )

#         mi = np.hstack(r[0] for r in results)
#         h = np.hstack(r[1] for r in results)

#         return np.nan_to_num(mi), np.nan_to_num(h)

    @staticmethod
    def _prepare(x, y, ui=None):

        if y.dtype != int and y.dtype != bool:
            raise ValueError("Y must belong to discrete classes of type `int' or type `bool'")

        variables = [np.copy(subx) for subx in x]
        targets = np.copy(np.atleast_2d(y))

        vrow, vcol = variables[0].shape[0], sum(subx.shape[1] for subx in variables)
        trow, tcol = targets.shape

        if trow == 1 and tcol == vrow:
            targets = targets.T
        elif tcol != 1 or trow != vrow:
            raise ValueError("`y' should have as many entries as `x' has rows.")

#         if ui is not None:
#             ui.complete.value *= 8

        return variables, targets, None
