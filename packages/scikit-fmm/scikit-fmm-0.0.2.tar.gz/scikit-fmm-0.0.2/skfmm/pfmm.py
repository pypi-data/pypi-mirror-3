import numpy as np

#import ipydb; ipydb.db()
#import sys; sys.exit()

__all__ = ['distance', 'travel_time']

from cfmm import cFastMarcher
from sys import float_info

FAR, NARROW, FROZEN, MASK = 0, 1, 2, 3


def pre_process_args(phi, dx):
    """
    get input data into the correct form for calling the c extension module
    This wrapper allows for a little bit of flexibility in the input types
    """
    if not isinstance(phi, np.ndarray):
        phi = np.array(phi)

    if type(dx) is float or type(dx) is int:
        dx = [dx for x in range(len(phi.shape))]
    dx = np.array(dx)

    if isinstance(phi, np.ma.MaskedArray):
        flag           = np.zeros(phi.shape, dtype=np.int)
        flag[phi.mask] = MASK
        phi            = phi.data
    else:
        flag = np.zeros(phi.shape, dtype=np.int)

    return phi, dx, flag


def post_process_result(result):
    """
    post-process results from the c module (add mask)
    """
    if (result == float_info.max).any():
        mask         = (result == float_info.max)
        result[mask] = 0
        result       = np.ma.MaskedArray(result, mask)
    return result


def distance(phi, dx=1.0, self_test=False):
    """
    Return the distance from the zero contour of the array phi.

    Parameters
    ----------
    phi : array-like
          the zero contour of this array is the boundary location for
          the distance calculation. Phi can of 1,2,3 or higher
          dimension and can be a masked array.

    dx  : float or an array-like of shape len(phi), optional
          the cell length in each dimension.

    self_test : bool, optional
                if True consistency checks are made on the binary min
                heap during the calculation. This is used in testing and
                results in a slower calculation.

    Returns
    -------
    d : an array the same shape as phi
        contains the distance from the zero contour (zero level set)
        of phi to each point in the array.
    """
    phi, dx, flag = pre_process_args(phi, dx)
    d = cFastMarcher(phi, dx, flag, None, int(self_test))
    d = post_process_result(d)
    return d


def travel_time(phi, speed, dx=1.0, self_test=False):
    """
    Return the travel from the zero contour of the array phi given the
    scalar velocity field speed.

    Parameters
    ----------
    phi : array-like
          the zero contour of this array is the boundary location for
          the travel time calculation. Phi can of 1,2,3 or higher
          dimension and can be a masked array.

    speed : array-like, the same shape as phi
            contains the speed of interface propagation at each point
            in the domain.

    dx  : float or an array-like of shape len(phi), optional
          the cell length in each dimension.

    self_test : bool, optional
                if True consistency checks are made on the binary min
                heap during the calculation. This is used in testing and
                results in a slower calculation.

    Returns
    -------
    t : an array the same shape as phi
        contains the travel time from the zero contour (zero level
        set) of phi to each point in the array given the scalar
        velocity field speed. If the input array speed has values less
        than or equal to zero the return value will be a masked array.
    """
    phi, dx, flag = pre_process_args(phi, dx)
    t = cFastMarcher(phi, dx, flag, speed, int(self_test))
    t = post_process_result(t)
    return t
