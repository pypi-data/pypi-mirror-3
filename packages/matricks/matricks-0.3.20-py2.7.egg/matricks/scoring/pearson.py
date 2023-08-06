from scorer import *

import ppmc

class Pearson(Scorer):
    """\
The score is the Pearson Product Moment Correlation between 
the reference vector (supplied when this class is instantiated)
and each vector submitted to the __call__ interface.  

The `ref`erence vector may be supplied as a literal list of values,
a profile (row) identifier, or row index (non-negative integer < len(mx)).

`null` is the value that should be used when either the min or max values cannot
be computed. This happens, for example, when the *low* or *high* list contain
only ``None`` values.
"""

    def __init__(self, mx, ref, null=None):

        if isinstance(ref, (list, tuple)):
            self.ref = ref

        elif isinstance (ref, (str, unicode)):
            row = mx.extractRows(ref)
            if row is None or len(row) == 0:  raise KeyError('reference vector not found: ' + ref)
            self.ref = row._data[mx.skiprows]

        elif isinstance(ref, (int)) and (ref >= 0):
            self.ref = mx._data[ref+mx.skiprows]

        else:
            raise TypeError ('Invalid type for reference vector: ' + str(type(ref)))

        self.ppmc = ppmc.PPMC(self.ref[mx.skipcols:])
        self.skip = mx.skipcols

    # The scoring function proper.
    def __call__(self, r, skip=0):
        return self.ppmc(r[self.skip:])

    
