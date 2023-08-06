from scorer import *

class Choi(Scorer):
    """\
The score is computed using Jarny Choi's "lowest of high - highest of low algorithm.

`low` and `high`, if specified, should be a sequence type of lists, strings, or regular
expresion (as in module `re`) objects.   In the last case, the expression will be applied
to all the labels (alal `getLabels` method) to form a (sub)group.

`thresh` is a floating point value that specifies the score lower bound.  
Expression profiles with a score below "thresh" will  not be included in the result
`Matricks`.

`agg` is a function used to aggregate the row values.  The default is the 
instance's default.

`null` is the value that should be used when either the min or max values cannot
be computed. This happens, for example, when the *low* or *high* list contain
only ``None`` values.
"""

    def __init__(self, mx, low=None, high=None, thresh=None, agg=None, null=None):
        # Make sure we have a low and high lists
        labels = mx.getLabels()[mx.skipcols:]
        if high is None: high = list(labels)
        if low is None: low = list(labels)
        
        # Supply an aggregator if none supplied explicitly.
        if agg is None: agg = mx._default_agg
        
        # Do we have a thresshold?
        if (thresh is not None) and not isinstance(thresh, (float, int)):
            thresh = None
            
        # Generate "comparand" functions for each of the top-level
        # elements in low and high lists.
        self.low_group =  [ mx.graep(ll, agg) for ll in low ]
        self.high_group =  [ mx.graep(ll, agg) for ll in high ]

    # The scoring function proper.
    def __call__(self, r, skip=1):
        low_bound = [ fn(r) for fn in self.low_group ]
        high_bound = [ fn(r) for fn in self.high_group ]
        
        return min(high_bound) - max(low_bound)

    
