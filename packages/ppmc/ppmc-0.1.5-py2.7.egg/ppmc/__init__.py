"""\

PPMC: Pearson Product Moment Correlation
========================================

An implementation of the Pearson Product Moment Correlation
calculation done on two python lists.   Assumes that a and b
are non-empty lists of numerics and are of equal length.

Return is a float between 0.0 (poorest correlation) and 1.0 (best
correlation).

This is modeled on the formula described in Wikipedia here:
Http://changingminds.org/explanations/research/analysis/pearson.htm

    r = SUM((xi - xbar)(y - ybar)) / ((n - 1) * sx * sy)

Where x and y are the variables, xi is a single value of x, 
xbar is the mean of all x's, n is the number of variables, and 
sx is the standard deviation of all x's.

To test:  run "python ppmc.py":

 >>> p = [1, 3, 5, 6, 8, 9, 6, 4, 3, 2]
 >>> q = [2, 5, 6, 6, 7, 7, 5, 3, 1, 1]

 >>> print round(calcPPMC(p, q), 4)
    0.8547

 >>> print round(calcPPMC(p, q, uncentered=True), 4)
    0.969

(Note: this uses the `sample standard deviation` rather than the
standard deviation of the sample.)

For cases where one vector is to be compared with a series of other
vectors, the `PPMC class` is provided which can be instantiated with the
*reference vector* that will be used in repeated, subsequent invocations
of the instance's ``__call__`` interface.  (See docstring for further details.)

In all cases, values of ``None`` will be excluded from the calculations, other than
serving as place-holders to determine the number of elements in a sequence to be
correlated.  For example, if a sequence is defined as

 >>> s1 = [ 1.0, None, 2.3 ]

The number of elements is 3, however, only the first and third will be included
in the calculations for mean, standard deviation, and so forth.

 >>> s2 = [ 1.0, 2.8, 0.9 ]
 >>> print round(calcPPMC(p, q), 4)
   0.8547

"""
    
__version__ = "0.1.5"

from math import sqrt

def calcPPMC(a, b, uncentered=False):
    """\
Returns the *Pearson Product Moment Correlation* between
two, equal-length sequences of numbers.

If the sequences lengths are not equal or of zero length, ``None`` 
is returned.
"""
    # Cull nulls.
    av = [ float(x) for x in a if x is not None ]
    bv = [ float(x) for x in b if x is not None ]
    
    # By making N a float, all the other numbers and calculations
    # that use it will be coerced to float.  This obviates the
    # need to iterate through the two incoming lists to ensure
    # their elements are all float.  They need only be numeric.
    N = len(a)

    # Sanity check: must be non-empty lists
    if N < 2 or N != len(b): return None   # Vectors are not same length.

    # Ensures all results will be float, later.
    N =float(N)  

    # Calc the means
    a_bar = 0.0 if uncentered else (sum(av) / N)
    b_bar = 0.0 if uncentered else (sum(bv) / N)
    
    # Calc the diffs from the mean (not the variances)
    a_diff = map(lambda x: x - a_bar, av)
    b_diff = map(lambda x: x - b_bar, bv)
    
    # Cal the sample std devs
    a_sdev = sqrt(sum(map(lambda x: x*x, a_diff)) / (N-1))
    b_sdev = sqrt(sum(map(lambda x: x*x, b_diff)) / (N-1))
    
    # Return the result.
    numerator =  ((N - 1) * a_sdev * b_sdev)
    return (sum(map(lambda x,y: (x * y), a_diff, b_diff)) / numerator) if numerator != 0.0 else -1.0


class PPMC(object):
    """\
Optimization suggested by Jarny Choi. 

Since we tend to use PPM to compare one vector against 45,000 or
so at a time, we can optmiize by creating a class that  initilizes
all the "a" stuff on instantiation, and then just pass the "b"s
via the call() interface.

Test with :

>>> p = [1, 3, 5, 6, 8, 9, 6, 4, 3, 2]
>>> q = [2, 5, 6, 6, 7, 7, 5, 3, 1, 1]

>>> c = PPMC(p)
>>> print round(c(q), 4)
0.8547

To compare this with other vectors, make repeated calls, passing
those vectors.

.. code-block:: python

>>> test_array = [
... [ 6.9267673364, 7.08285858295, 7.15055382403, 7.03541702514, 7.11506712259, 7.15041742796, 7.05878177275 ], 
... [ 6.58587973227, 6.65782136649, 6.62314489813, 6.54883622289, 6.47511118167, 6.49239723003, 6.46336715379 ], 
... [ 6.54973055245, 6.67584083418, 6.63965139555, 6.67821866477, 6.72783189441, 6.66759063928, 6.56705206299 ], 
... [ 6.5402492892, 6.69181362344, 6.57972709429, 6.58134625476, 6.52698595154, 6.61928404895, 6.70371761591 ], 
... [ 6.82583507351, 6.61887153183, 6.76668680385, 6.71780977921, 6.72533423069, 6.86479656749, 6.6784677948 ], 
... [ 6.78868472579, 6.70541826437, 6.67059629504, 6.71173630229, 6.69792152141, 6.71825130309, 6.62542732319 ], 
... [ 7.24626409224, 7.39260390178, 7.07453296577, 7.0838446862, 7.29543821623, 7.30116491458, 7.15711346105 ], 
... [ 6.71927054931, 6.69492551656, 6.6814832304, 6.55587328826, 6.70885768235, 6.56817831265, 6.69203010225 ], 
... [ 6.67815422925, 6.65748403271, 6.67916497857, 6.67153058933, 6.73581504374, 6.65949463364, 6.63428387224 ], 
... [ 6.53937313644, 6.61721082254, 6.63096969414, 6.68743718644, 6.72850696328, 6.69802077819, 6.56161028181 ], 
... [ 6.53931932014, 6.70817097627, 6.71661658482, 6.67828462681, 6.63797236382, 6.69512396679, 6.7776795476 ], 
... [ 6.53964438774, 6.69429773546, 6.67363600859, 6.75134862519, 6.69460548473, 6.67740635951, 6.61441693307 ], 
... [ 7.37901208327, 7.72221650609, 7.42013009957, 7.38939957847, 7.45423862834, 7.34834536669, 7.56569064612 ], 
... [ 6.89929105186, 6.67473294675, 6.5622798898, 6.59396005297, 6.68714569441, 6.62256250045, 6.65658876708 ], 
... [ 7.98729751374, 7.09890372127, 7.39735831535, 7.19746897763, 7.18789214396, 7.15117464436, 7.05072067994 ], 
... [ 6.78604996868, 6.73708411577, 6.8016606204, 6.89660555562, 6.8199729144, 6.8866635094, 6.8306270266 ], 
... [ 6.60174679429, 6.74342944423, 6.73358852283, 6.79356276786, 6.82427379835, 6.92925427311, 6.63733468757 ], 
... [ 6.75672500507, 6.55031660629, 6.61675190132, 6.57680657541, 6.74698160475, 6.72608725898, 6.5866878238 ], 
... [ 8.71782257104, 9.31647370195, 9.64377703619, 9.43821240004, 9.0544779487, 8.93213504795, 9.11532203593 ], 
... [ 6.82856483633, 6.82002643115, 6.78617491081, 7.01654277114, 6.93667577906, 7.41680038577, 7.02593139137 ], 
... ]
 
>>> p = PPMC(test_array[0])
>>> for r in test_array[1:]:
...     print round (p(r), 5)
    -0.13537
    0.62854
    0.17336
    -0.02381
    -0.56928
    0.03604
    -0.25743
    0.11956
    0.63927
    0.62009
    0.59425
    0.05665
    -0.80645
    -0.68099
    0.1838
    0.71158
    -0.13361
    0.48407
    0.34852

"""

    def __init__(self, a, uncentered=False):

        self._a = [ x for x in a if x is not None ]
        self._N = float(len(a)) if len(a) > 1 else None
        self._uncentered = (uncentered == True)
        self._a_bar = 0.0 if self._uncentered else (sum(self._a) / self._N)
        self._a_diff = map(lambda x: x - self._a_bar, self._a)
        self._a_sdev = sqrt(sum(map(lambda x: x**2, self._a_diff)) / (self._N-1))

    def __call__ (self, b):
        if self._N is None or len(b) != self._N: return None

        bv = [ x for x in b if x is not None ]
        
        b_bar = 0.0 if self._uncentered else (sum(bv) / self._N)
        b_diff = map(lambda x: x - b_bar, bv)
        b_sdev = sqrt(sum(map(lambda x: x**2, b_diff)) / (self._N-1))
        
        numerator = ((self._N - 1) * self._a_sdev * b_sdev)
        return (sum(map(lambda x,y: (x * y), self._a_diff, b_diff)) / numerator) if numerator != 0 else -1.0


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    


                                    
