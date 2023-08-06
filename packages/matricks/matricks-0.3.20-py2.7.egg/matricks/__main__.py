import logging
log = logging.getLogger('sample')

import re
import sys
import optparse
import cfgparse

import time

sys.path.extend(('..', '.'))

import matricks

default_cfg = """\
[DEFAULT]

"""


log_levels = {
    'DEB': logging.DEBUG,
    'INF': logging.INFO,
    'WAR': logging.WARN,
    'ERR': logging.ERROR,
    'CRI': logging.CRITICAL,
    'FAT': logging.FATAL,
    }

converters = {
    'float': float,
    'int': int, 'integer': int,
    'upper': lambda x: x.upper(),
    'lower': lambda x: x.lower(),
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
    c = cfgparse.ConfigParser()
    log.info('option and command line parsers created')

    # Tell the config parser to look on the command line for cfg file names and keys
    c.add_file(content=default_cfg)
    c.add_optparse_files_option(o)
    c.add_optparse_keys_option(o)
    log.info('file and keys options processed')

    # Global (i.e. DEFAULT) run-time options
    # The actual values for these may depend on the
    # section (key) being processed.  
    o.add_option('-i', '--input', type=None, help='PATH to input')
    input = c.add_option('input', type='string',  default=None)
    o.add_option('-o', '--output', type=None, help='PATH to output')
    output = c.add_option('output', default=None)
    o.add_option('-P', '--prefix', help='PATH to prefix to filenames')
    prefix = c.add_option('prefix', default='.')
    o.add_option('-v', '--verbose', action='store_true', help='turn on verbose logging')
    verbose = c.add_option('verbose', default=False)
    o.add_option('-f', '--format', help='specify output format:  [s]hort, [t]sv, [c]sv, or [j]son. Default: short')
    verbose = c.add_option('format', default='short')
    o.add_option('--null', help='string to be interpreted as null data [None (object)]')
    null_data = c.add_option('null', default=None)
    o.add_option('--fsep', help='Field delimitter character [\\t]')
    fsep = c.add_option('fsep', default='\t')
    o.add_option('--rsep', help='Row/record delimitter character [\\n]')
    rsep = c.add_option('rsep', default='\n')
    o.add_option('--skipcols', help='number of columns that ar non-data [1]')
    skipcols = c.add_option('skipcols', type='int', default=1)
    o.add_option('--skiprows', help='number of columns that ar non-data [1]')
    skiprows = c.add_option('skiprows', type='int', default=1)
    o.add_option('-d', '--debug', default='WARN', help="debug level (" + "|".join(log_levels.keys()) + ")")
    dbg_lvl = c.add_option('debug')
    o.add_option('-T', '--timing', action='store_true',  help='display timing data')
    timing = c.add_option('timing', default=False)
    o.add_option('-C', '--convert', help='specify conversion of elements not in skipcols or skiprows (' + "|".join(converters.keys()) + ")")
    timing = c.add_option('timing', default=False)

    opts, args = c.parse(o)

    # Make sure we have minimal information to work with
    #if opts.help is not None:
    #    o.print_help()
    #    c.print_help()
    #    return 1

    #dict_dump(c.option_dicts)  ## DEBUG
    log.setLevel(log_levels.get(dbg_lvl.get().upper()[:4], 'WARN'))

    log.info('command line and config file(s) processed')
    log.info('begin main processing')

    if opts.input is None or len(opts.input) < 1:
        if timing: t0 = time.time()
        input = [ x.split(fsep) for x in [ l.split(rsep) for l in sys.stdin.read() ] ]
        if timing: log.info('matricks source inhaled in %6.4f s' % (time.time() - t0))
    
    if timing: t0 = time.time()
    conv = converters[opts.convert.lower()] if opts.convert is not None and opts.convert.lower() in converters.keys() else None
    inMx = matricks.Matricks(opts.input, 
                             fsep=opts.fsep, rsep=opts.rsep,
                             skipcols=opts.skipcols, skiprows=opts.skiprows,
                             cvt=conv)
    if timing: log.info('matricks created in %6.4f s' % (time.time() - t0))

    if timing: t0 = time.time()
    if opts.output is None or len(opts.output) < 1:
        output = sys.stdout
    else:
        output = open(opts.output, 'w')
    
    formatted = formatters.get(opts.format[0].lower(), formatters.get('s'))
    output.write(formatted(inMx))
    if timing: log.info('matricks spewed in %6.4f s' % (time.time() - t0))

    return 0
        
if __name__ == '__main__':
    sys.exit(main())
