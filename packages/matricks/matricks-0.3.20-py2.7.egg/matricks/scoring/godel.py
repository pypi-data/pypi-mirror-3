
from scorer import *

import math
import primes

class GodelPositional(Scorer):
    """\
Godel Positional Scoring

Score is computed by identifying extrema values and marking their
position in a "shadow" vector the corresponds with a 2 for maxima, a 1
for minima, and 0 for all non-extreme values.
Each position in this vector is
then assigned a unique prime number raised to the power indicated in the
shadow vector for that position.  (Only positions with a 1 or a 2 will 
see any real contribution to the product.  The primes of the non-zero elements
of this vector are multiplied together to create a product that
represents the extrema pattern for each profile.   Profiles may then be sorted
using this product as a sort key, which will result in profiles with greater 
similarity to one another being grouped closer together in the sort.

Whether or not a value is an extrema is determined by comparing it to the
mean of the profile to see if it is within some multiple (the `c` argument)
of the standard deviation of the profile.   (Mean and std dev are computed for
each profile before scoring takes place.)

"""
    
    def __init__(self, mx, C=1, modal=False, prec=None, **kwargs):
        self.mx = mx
        self.C = C
        self.modal = (modal == True)
        self.prec = int(math.log(len(mx.labels[mx.skipcols:]))) if prec is None else prec
        #print self.prec
        self.prime_map = dict(zip(mx.labels[mx.skipcols:], primes.first1000))

    @staticmethod
    def signum(n):
        return 1 if n < 0 else 2

    def __call__(self, v, skip=1):
        
        # Sort the non-null elements of v.
        vec = sorted([ (self.mx.labels[i],v[i], i) for i in range(len(v)) if isinstance(v[i], (float, int))],
                     key=lambda x: x[1], reverse=True)

        # Skim off the elements that fall above the cut-off.
        top = list()

        if self.modal:   # Cut-off is the mode.
            mode = self.mx.mode(v, prec=self.prec)
            top = [ e for e in vec if e[1] > mode ]

        else: # Cut-off is the mean + some multiple of the std dev.
            mean, std_dev = self.mx.std_stats([vec[i][1] for i in range(len(vec)) ])
            top = [ e for e in vec if e[1] > mean + (self.C * std_dev) ]

        # We got nuthin'.
        if len(vec) < 1: 
            return None

        # Take as many elements off the low end of this same list.
        # (If the "top" list is empty then vec is probably empty, too.)e
        top_len = len(top)
        if top_len == 0: 
            return None

        bottom = [x for x in vec[-top_len:]]

        result = reduce (lambda x, i: x * (self.prime_map[top[i][0]] ** 2) * \
                             self.prime_map[bottom[i][0]], 
                         range(top_len), 1)
        #print result
        return result
    
