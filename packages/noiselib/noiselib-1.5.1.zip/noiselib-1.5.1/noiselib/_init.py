# Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
# see LICENSE.txt for details



from _simplex import set_perm
from random import randint



######################################################################
def main(period = None, perm = None):
    """
period : the integer inverval in which the noise repeats.  it should
    be a power of two.  period and permutation table cannot be
    specified together

permutation table : an interable sequence of integers with power of
    two length and no integer larger than period - 1.
    period and permutation table cannot be specified
    together.
    """
    if period and perm: raise ValueError(
        'Can specify either period or permutation_table, not both')
    # permuation table is doubled to eliminate additional wrapping of indices
    elif period: set_perm(_make_perm(period) * 2)
    elif perm: set_perm(tuple(perm) * 2)
    else: raise ValueError('Require either period or permutation_table')

def _make_perm(period):
    perm = range(period)
    _perm_ = xrange(period)
    period_n = period - 1
    for i in _perm_:
        j = randint(0, period_n)
        perm[i], perm[j] = perm[j], perm[i]
    return tuple(perm)
