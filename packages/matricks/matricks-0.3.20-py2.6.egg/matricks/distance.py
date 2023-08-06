
"""\
Distance Functions
------------------

"""


from math import sqrt, pow

NaN = float('nan')

def pearson(a, b, uncentered=False, absolute=False):
    """\
Returns the *Pearson Product Moment Correlation* between
two, equal-length sequences of numbers.

If the sequences lengths are not equal or of zero length, ``None`` 
is returned.

Note this can be used for the absolute, uncentered, and uncentered absolute
versions of this calculation.  (See Matricks.distance for more info.)

                                        absolute         uncentered
                                        ----------------------------------
    pearson correlation:                False,           False  (Default)
    absolute pearson correlation:       True             False
    uncentered pearson correlation:     False            True
    absolute uncentered pearson corr:   True             True
"""
    # Cull nulls.
    av = [ float(x) for x in a if x is not None ]
    bv = [ float(x) for x in b if x is not None ]
    
    # By making N a float, all the other numbers and calculations
    # that use it will be coerced to float.  This obviates the
    # need to iterate through the two incoming lists to ensure
    # their elements are all float.  They need only be numeric.
    N = len(av)

    # Sanity check: must be non-empty lists
    if N < 2 or N != len(bv): return NaN   # Vectors are not same length.

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
    numerator = (a_sdev * b_sdev * (N-1))
    ppm = (sum(map(lambda x,y: x * y, a_diff, b_diff)) / numerator) if numerator != 0.0 else 0.0

    return 1 - (abs(ppm) if absolute else ppm)



def spearman(a, b):
    """\
Spearman's Rank correlation distance.
"""
    # Note:  the use of enumerate(), below, replaces the construct [ (i, list[i]) for i in range(len(list)) ]
    av = [ x[0]+1 for x in sorted(enumerate(a), key=lambda x: x[1]) ]
    bv = [ x[0]+1 for x in sorted(enumerate(b), key=lambda x: x[1]) ]

    return pearson(av, bv)


def euclideanDistance(a, b):
    """\
Euclidean distance between two vectors, *a* amd *b* .
"""
    vec = [pow(a[i] - b[i], 2) for i in range(len(a)) if None not in [a[i],b[i]]]
    return (sum(vec) / len(vec)) if len(vec) > 0 else NaN

def blockDistance(a, b):
    """\
City-block (aka Manhattan)  distance between two vectors, *a* amd *b* .
"""
    #vec = [abs(a[i] - b[i]) for i in range(len(a)) if None not in [a[i],b[i]]]
    vec = [abs(x[0] - x[1]) for x in zip(a, b) if None not in x ]
    return (sum(vec) / len(vec)) if len(vec) > 0 else NaN


def  kendallsTau(a, b):
    """
Based on http://en.wikipedia.org/wiki/Kendall_tau_distance

Count up the number of discordant pairs and divide these by the
number of possible pairings. (n * (n - 1)) / 2)

disconrdant <- (x[i] < x[j] and y[i] > y[j]) or (x[i] > x[j] and y[i] < y[j])

"""
    # Calculate the numerator.
    numerator = 0
    sgn = lambda x: -1 if x < 0 else (1 if x > 0 else 0)
    N = len(a)
    if N < 2 or N != len(b): return NaN

    for i in range(len(a)-1):
        j = i+1
        if None not in [ a[i], a[j], b[i], b[j] ]:
            if (a[i] < a[j] and b[i] > b[j]) or (a[i] > a[j] and b[i] < b[j]): # discordant
                numerator = numerator + 1

    # And the denominator
    return float(numerator) / ((N * (N - 1)) / 2.0)
            
