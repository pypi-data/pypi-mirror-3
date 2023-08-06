# -*- coding: utf-8 -*
from __future__ import division
import numpy as np
from scipy import stats
from scipy import __version__ as scipy_version

_chk_asarray = stats.stats._chk_asarray

def spearmanr(a, b=None, axis=0):
    '''A Spearman rank-order correlation coefficient that handles ties correctly. A correct version is provided in Scipy 0.8.
    
This code from http://projects.scipy.org/pipermail/scipy-user/2009-January/019198.html

    Parameters
    ----------
    a, b : 1D or 2D array_like, b is optional
    
        One or two 1-D or 2-D arrays containing multiple variables and
        observations. Each column of m represents a variable, and each row
        entry a single observation of those variables. Also see axis below.
        Both arrays need to have the same length in the `axis` dimension.
        
    axis : int or None, optional
        If axis=0 (default), then each column represents a variable, with
        observations in the rows. If axis=0, the relationship is transposed:
        each row represents a variable, while the columns contain observations.
        If axis=None, then both arrays will be raveled
        

    Returns
    -------
    
    rho: float or array (2D square)
        Spearman correlation matrix or correlation coefficient (if only 2 variables
        are given as parameters. Correlation matrix is square with length
        equal to total number of variables (columns or rows) in a and b
        combined

    t: float or array (2D square)
        t-statistic for Null hypothesis of no correlation, has same
        dimension as rho

    p-value: float or array (2D square)
        p-value for the two-sided test, has same dimension as rho

    Notes
    -----

    main changes to existing stats.spearmanr
    * correct tie handling
    * calculates correlation matrix instead of only single correlation
      coeffiecient,
      similar to np.corrcoef but using keyword argument axis=0 (default)
    * returns also t-statistic (can be dropped for backwards compatibility)
    * open question, zero division
        >>> stats.spearmanr([1,1,1,1],[1,1,1,1])
        (1.0, 0.0)
        >>> stats.spearmanr([1,1,1,1],[2,2,2,2])
        (1.0, 0.0)
        >>> spearmanr([1,1,1,1],[2,2,2,2])
        (-1.#IND, -1.#IND, 0.0)
        >>> spearmanr([1,1,1,1],[1,1,1,1])
        (-1.#IND, -1.#IND, 0.0)
        >>> np.corrcoef([1,1,1,1],[2,2,2,2])
        array([[ NaN,  NaN],
               [ NaN,  NaN]])

    comparison to stats.mstats.spearmanr
    * both have correct tie handling
    * mstats.spearmanr
      - ravels if more than 1 variable per array
      - calculates only one correlation coefficient, no correlation matrix
      - uses masked arrays

    difference to np.corrcoef
    * using keyword argument axis=0 (default), instead of rowvar=1
    * returns one correlation coefficient for two variables, instead of
      2 by 2 matrix

    comparison to R
    * identical correlation matrix if only one array given
    * if 2 arrays are given, then R only calculates cross-correlation
    * p-value is the same as in R with exact=False

    Examples
    --------

    >>> spearmanr([1,2,3,4,5],[5,6,7,8,7])
    (0.82078268166812329, 2.4886840673530211, 0.088587005313543798)
    >>> np.random.seed(1234321)
    >>> x2n=np.random.randn(100,2)
    >>> y2n=np.random.randn(100,2)
    >>> spearmanr(x2n)
    (0.059969996999699973, 0.59474311216315867, 0.55338590803773591)
    >>> spearmanr(x2n[:,0], x2n[:,1])
    (0.059969996999699973, 0.59474311216315867, 0.55338590803773591)
    >>> rho, t, pval = spearmanr(x2n,y2n)
    >>> rho
    array([[ 1.        ,  0.05997   ,  0.18569457,  0.06258626],
           [ 0.05997   ,  1.        ,  0.110003  ,  0.02534653],
           [ 0.18569457,  0.110003  ,  1.        ,  0.03488749],
           [ 0.06258626,  0.02534653,  0.03488749,  1.        ]])
    >>> t
    array([[        Inf,  0.59474311,  1.87082067,  0.62078937],
           [ 0.59474311,         Inf,  1.0956232 ,  0.25099853],
           [ 1.87082067,  1.0956232 ,         Inf,  0.34557889],
           [ 0.62078937,  0.25099853,  0.34557889,         Inf]])
    >>> pval
    array([[ 0.        ,  0.55338591,  0.06435364,  0.53617935],
           [ 0.55338591,  0.        ,  0.27592895,  0.80234077],
           [ 0.06435364,  0.27592895,  0.        ,  0.73039992],
           [ 0.53617935,  0.80234077,  0.73039992,  0.        ]])
    >>> rho, t, pval = spearmanr(x2n.T, y2n.T, axis=1)
    >>> rho
    array([[ 1.        ,  0.05997   ,  0.18569457,  0.06258626],
           [ 0.05997   ,  1.        ,  0.110003  ,  0.02534653],
           [ 0.18569457,  0.110003  ,  1.        ,  0.03488749],
           [ 0.06258626,  0.02534653,  0.03488749,  1.        ]])
    >>> spearmanr(x2n,y2n, axis=None)
    (0.10816770419260482, 1.531037630064956, 0.1273562188027364)
    >>> stats.spearmanr(x2n.ravel(),y2n.ravel())
    (0.1081677041926048, 0.12735621880273479)
    >>> spearmanr(x2n.ravel(),y2n.ravel())
    (0.10816770419260482, 1.531037630064956, 0.1273562188027364)
    
    >>> xint = np.random.randint(10,size=(100,2))
    >>> spearmanr(xint)
    (0.052760927029710199, 0.52303502765353049, 0.60213045837062351)
    >>> stats.spearmanr(xint)
    Traceback (most recent call last):
      File "<pyshell#202>", line 1, in <module>
        stats.spearmanr(xint)
    TypeError: spearmanr() takes exactly 2 arguments (1 given)
    >>> stats.spearmanr(xint[:,0],xint[:,1]) #no tie handling
    (0.064461446144614465, 0.52401200405558157)    
    '''
    # Check if correct version is present
    major, minor = scipy_version.split(".")[:2]
    if int(major) >= 1 or int(minor) >= "8":
        return stats.stats.spearmanr(a, b, axis)
    
    a, axisout = _chk_asarray(a, axis)
    ar = np.apply_along_axis(stats.rankdata,axisout,a)
    
    br = None
    if not b is None:
        b, axisout = _chk_asarray(b, axis)
        br = np.apply_along_axis(stats.rankdata,axisout,b)
    n = a.shape[axisout]
    rs = np.corrcoef(ar,br,rowvar=axisout)

    t = rs * np.sqrt((n-2) / ((rs+1.0)*(1.0-rs)))
    prob = stats.t.sf(np.abs(t),n-2)*2
    
    if rs.shape == (2,2):
        return rs[1,0], t[1,0], prob[1,0]
    else:
        return rs, t, prob

