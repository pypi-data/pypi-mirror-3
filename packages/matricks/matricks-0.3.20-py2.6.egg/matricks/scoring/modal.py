
from scorer import *

import primes

class ModalPositional(Scorer):
    """\
Modal Scoring

Score is computed by identifying extrema values and marking their
position in a "shadow" vector the corresponds with 2 or 1 if
the value falls outside of the mode of the vector +/- some threshold (default: 0)
Each position in this vector is
then assigned a unique prime number raised to the power indicated in the
shadow vector for that position.  (Only positions with a 1 or a 2 will 
see any real contribution to the product.  The primes of the non-zero elements
of this vector are multiplied together to create a product that
represents the extrema pattern for each profile.   Profiles may then be sorted
using this product as a sort key, which will result in profiles with greater 
similarity to one another being grouped closer together in the sort.
"""
    
    def __init__(self, mx, thresh=0, prec=0, **kwargs):

        self.mx = mx
        self.thresh = thresh
        self.prec = prec


    @staticmethod
    def signum(n):
        return 1 if n < 0 else 2

    def __call__(self, v, skip=1):
        # Build a list of rows that are not "flat-liners".
        # A flat-linter is a row in which all of the values
        # are either None or are within c * stddev of the mean 
        # for that row.

        mode = self.mx.mode(v, self.prec)
        vec = [ (self.signum(e - mode) if (abs(e - mode) > self.thresh) else 0) for e in v[skip:] ]

        return reduce (lambda x, y: x * (y[0] ** y[1]), zip(primes.first1000, vec), 1)

    
