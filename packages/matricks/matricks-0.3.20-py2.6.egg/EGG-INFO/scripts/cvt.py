"""\
Functions / classes for converting raw datasets into Matricks instances.
"""

import logging
logging.basicConfig()
log = logging.getLogger('cvt')

import optparse
import sys
import os
import cPickle

import matricks
import re

def cvtfloat(file, **kwargs):
    """\
Convert raw dataset contained in ``file`` to a Matricks instance in which all of the columns to the
right of the `skipcols` columns are converted to ``float`` data type.

"""
    def _cf(x):
        """\
        Attempt to convert string to float.  Returns either the float version or ``None``
        if conversion fails.
        """
        try:
            return float(x)
        except:
            return None

    raw = [ [ r.strip() for r in x.split(kwargs.get("fsep",'\t'))] \
                for x in re.split(kwargs.get("rsep", "\r[^\n]|\n|\r\n"), open(file, 'r').read()) ]

    if not kwargs.has_key('cvt'): kwargs['cvt'] = _cf
    md = matricks.Matricks(raw, **kwargs)

    return md


log_levels = {
    'DEB': logging.DEBUG,
    'INF': logging.INFO,
    'WAR': logging.WARN,
    'ERR': logging.ERROR,
    'CRI': logging.CRITICAL,
    'FAT': logging.FATAL,
    }

formatters = {
    's': lambda m: repr(m), 
    't': lambda m: m.dumps(fsep='\t', rsep='\n'),
    'c': lambda m: m.dumps(fsep=',', rsep='\n'),
    'j': lambda m: m.json(),
}

def main():

    # Initialize    
    # Get options
    o = optparse.OptionParser()
    log.info('option and command line parsers created')

    # Global (i.e. DEFAULT) run-time options
    # The actual values for these may depend on the
    # section (key) being processed.  
    o.add_option('-i', '--input', type=None, help='PATH to input FILE', dest="input", metavar="FILE", default=None)
    o.add_option('-o', '--output', type=None, help='PATH to output FILE', dest="output", metavar="FILE", default=None)
    o.add_option('-P', '--prefix', help='PATH to prefix to filenames', type='string', default='', metavar="PATH", dest="prefix")
    o.add_option('-v', '--verbose', action='store_true', help='turn on verbose logging', type=None, default=False, dest="verbose")
    o.add_option('--fsep', help='Field delimitter CHAR [\\t]', type='string', default='\t', dest="fsep", metavar="CHAR")
    o.add_option('--rsep', help='Row/record delimitter CHAR [\\n]', type='string', default='\r[^\n]|\n|\r\n', dest="rsep", metavar="CHAR")
    o.add_option('--skipcols', help='NUMBER of columns that ar non-data [1]', type='int', default=1, dest="skipcols", metavar="NUMBER")
    o.add_option('--skiprows', help='NUMBER of columns that ar non-data [1]', type='int', default=1, dest="skiprows", metavar="NUMBER")
    o.add_option('-d', '--debug', default='WARN', help="debug LEVEL (" + "|".join(log_levels.keys()) + ")", dest="dbg_lvl", metavar="LEVEL")

    opts, args = o.parse_args(sys.argv)

    # Make sure we have minimal information to work with
    #if len(args) < 2 and opts.input is None:
    #    o.print_help()
    #    return 1

    #dict_dump(c.option_dicts)  ## DEBUG
    log.setLevel(log_levels.get(opts.dbg_lvl.upper()[:3], 'WAR'))

    log.info('command line and config file(s) processed')
    log.info('begin main processing')

    rd_in = args[1] if len(args) > 1 else opts.input
    if rd_in is None:
        o.print_help()
        return 1

    rd = cvtfloat(rd_in, skipcols=opts.skipcols, skiprows=opts.skiprows,
                  fsep=opts.fsep, rsep=opts.rsep)

    rd_of = opts.output if opts.output is not None else os.path.splitext(rd_in)[0] + '.P'

    cPickle.dump(rd, open(rd_of, 'w'), -1)

    return 0

if __name__ == "__main__":
    main()
