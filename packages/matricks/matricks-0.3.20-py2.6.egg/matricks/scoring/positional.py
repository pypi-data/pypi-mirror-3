
from scorer import *

import math

class Positional(Scorer):
    """\
Positional Scoring

Score is computed by identifying extrema values and marking their
position in a "shadow" vector that uses the index for maxima and the negated
index for minima.  These vectors can then be passed to the `sorted` python 
built-in funciton and sorted lexicographically to group like profiles
together.

Whether or not a value is an extrema is determined by comparing it to the
mean of the profile to see if it is within some multiple (the `c` argument)
of the standard deviation of the profile.   (Mean and std dev are computed for
each profile before scoring takes place.)

"""
    
    def __init__(self, mx, C=1, modal=False, prec=None, thresh=None, **kwargs):
        self.mx = mx
        self.C = C
        self.modal = (modal == True)
        self.prec = int(math.log(len(mx.labels[mx.skipcols:]))) if prec is None else prec
        #print self.prec
        self.thresh = thresh   # Threshold calculation function
        self.position_map = dict(zip(mx.labels, range(len(mx.labels))))

    @staticmethod
    def signum(n):
        return 1 if n < 0 else 2

    def __call__(self, v, skip=1, prec=None):
        
        # Sort the non-null elements of v.
        vec = sorted([ (self.mx.labels[i],v[i], i) for i in range(len(v)) if isinstance(v[i], (float, int))],
                     key=lambda x: x[1], reverse=True)

        # Skim off the elements that fall above the cut-off.
        top = list()

        if self.modal:   # Cut-off is the mode.
            mode = self.mx.mode(v, prec=self.prec)
            top = [ e for e in vec if e[1] > mode ][:self.C]

        elif self.thresh is not None:
            th = self.thresh([ e[1] for e in vec], prec=(self.prec if prec is None else prec))
            top = filter (lambda e: e[1] > th, vec)

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
            #return None
            return tuple([len(v)+1]*len(v))

        result =  tuple([ x[2] for x in top])

        #print result

        return sorted(result)

