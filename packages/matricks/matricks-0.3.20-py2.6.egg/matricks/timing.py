import sys

sys.path.append('..')

import re
import matricks
import time
import random

def timing(dataset, output=None, rsep='\n', fsep='\t', 
           cvt=None, null=None,
           skiprows=1, skipcols=1,
           aggfn=None):

    if cvt is None:  
        cvt = lambda x: float(x) if x[0] in '+-0123456789.' else (None if x == null else x)

    ctpat = re.compile(r'([\w\_\+\-]+)(\.\w+)?')
    ctfn = lambda x: ctpat.match(x).group(1)
    
    # Load ...
    t0 = time.time()
    csl = matricks.Matricks(dataset, rsep=rsep, fsep=fsep,
                                       skiprows=skiprows, skipcols=skipcols,
                                       cvt=cvt)
    t1 = time.time()
    print 'loaded', len(csl), 'records in', t1 - t0, 'sec'
    
    # Aggregation ...
    if aggfn:
        t0 = time.time()
        csl_ct = csl.aggregate(aggfn)
        t1 = time.time()
        print 'aggregated', len(csl.getLabels()), 'samples into',len(csl_ct.getLabels()),'in', t1 - t0, 'sec'
    
    # Random profile retrieval
    t0 = time.time()
    
    for i in range(10):
        x = [y for y in csl][random.randint(0,len(csl))]
        p = csl.pearson(x[0])
    t1 = time.time()
    
    print '10 random profiles chosen and ppm correlated in', t1 - t0, 'sec'
        
    if output is None:
        output = sys.stdout

    t0 = time.time()
    csl.dump(output)
    t1 = time.time()
    print len(csl),'written to',output,'in',t1-t0,'sec'
    
    
