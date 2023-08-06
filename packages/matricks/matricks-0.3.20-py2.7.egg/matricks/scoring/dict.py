from scorer import *

class Dict(Scorer):
    """\
This scorer uses a dictionary to return a scalar score that can be used
for sorting purposes.  The initial motivation for this was to be able to arrange
heatmaps by rows (which equated to cell types) such that similar cell types
would be positioned close to one another.  (B cell types all together in one
group, for example.)

`mapping` can be a list or a dictionary that maps names to discreet scores.
 If `mapping` is a list, it can contain either strings or positive integer
values and will be used to create a dictionary that maps names to indexes.  For 
numeric elements, the name of the corresponding row will become the dictionary key 
with the value being the value of that element.  For strings the value will be
The labels will be mapped to column indexes in order to save that step during the actual
scoring process (i.e., in __call__.)

`default_score` is the score that should be returned if a label or index is supplied
that doesn't exist in the mapping or in the dataset.  This defaults to ``None``, 
which effects a behaviour similar to other `Scorer` classes.

`null` is the value that should be used when either the min or max values cannot
be computed. This happens, for example, when the *low* or *high* list contain
only ``None`` values.

"""

    def __init__(self, mx, mapping, default_score=None, null=None):
        if not isinstance(mapping, dict):
            raise TypeError('mapping argument is not a mapping type' + str(mapping))

        self.mx = mx
        self._dflt = default_score

        if isinstance(mapping, dict):
            self._mapping = mapping

        elif isinstance(mapping, (list, tuple, set)):
            self._mapping = dict()
            for i in range(len(mapping)):
                me = mapping[i]
                if isinstance(me, (str, unicode)):
                    self._mapping[me] = i if (me in self.mx.labels) else self._dflt

                elif isinstance(me, int) and me > 0:  # (we don't include the first element of any row)
                    self._mapping[mx.labels[me]] = i if (me < len(mx.labels)) else self._dflt
                    
                else:
                    raise TypeError('mapping elements must be str, unicode, or positive int.')

        else:
            raise TypeError('mapping must be a mapping or sequence type')


    # The scoring function proper.  (Not much to this at all, is there?)
    def __call__(self, r, skip=1):
        return self._mapping.get(r[0], self._dflt)

    
