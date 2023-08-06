import logging

log = logging.getLogger(__name__)

from scorer import *

import math
import primes

class HiLoPositional(Scorer):
    """\
Hi-Lo Positional Scoring

Score is computed by identifying extrema values and marking their
position in a "shadow" vector the corresponds with a '2' for high values,
a '1' for low values, and 0 for values that do not qualify as extrema.
A string is constructed by concatenating these values to produce a (possibly
VERLY long) sort key.

Sorting this will result in profiles with greater 
similarity to one another being grouped closer together in the sort.

Whether or not a value is an extrema is determined by comparing it to the
mean of the profile to see if it is within some multiple (the `c` argument)
of the standard deviation of the profile.   (Mean and std dev are computed for
each profile before scoring takes place.)

If non-null, the value of the `extrema` argument is used as a threshold for the
number of allowed peaks in the sample.  If the number of extrema (i.e.
the number of 1's in the shadow vector) exceeds this number, the profile
is regarded as a "flat-line" and is omitted form the result set.  By default, this
threshold is the number of data columns (i.e., columns beyind the first *skipcols* 
columns) in the instance.
"""
    
    def __init__(self, mx, C=1, modal=False, thresh=None, prec=None, **kwargs):

        self.mx = mx
        self.C = C
        self.modal = (modal == True)
        self.thresh = thresh if isinstance(thresh, int) else len(mx.labels)
        self.prec = int(math.log(len(mx.labels[mx.skipcols:]))) if prec is None else prec
        #print self.prec, self.thresh


    @staticmethod
    def signum(n):
        return '0' if n < 0 else '1'


    def __call__(self, v, skip=1):
        # Build a list of rows that are not "flat-liners".
        # A flat-linter is a row in which all of the values
        # are either None or are within c * stddev of the mean 
        # for that row.
        
        if self.modal:
            baseline = self.mx.mode(v, prec=self.prec)
            test = baseline + self.thresh
        else:
            baseline, std_dev = self.mx.std_stats(v)
            test = self.C * std_dev

        # Sort the non-null elements of v.
        vec = [ (self.mx.labels[i],v[i]) for i in range(len(v)) if isinstance(v[i], (float, int))]
        vec = sorted(vec, key=lambda x: x[1], reverse=True)

        # Skim off the elements that fall above the cut-off.
        top = [ e[0] for e in vec[:self.thresh] if e[1] > test ]
        top_len = len(top)
        if top_len == 0: return None

        # Take as many elements again from the "low" end of the list
        top.extend([ e[0] for e in vec[-top_len:]])
        #print 'len(top):', len(top), 'len(v):',len(v)

        result = ":".join(top)

        return result

    
