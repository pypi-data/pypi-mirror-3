"""\
Conversion Director
===================

Class that provides a set of conversions for ``Matricks`` instantiation.

Initially, ``Matricks`` instances created from text input used a global
conversion function, such as the ``float`` class constructor, in conjunction
with the ``skipcols`` option to tell the constructor how many of the left-most columns
to skip before starting to apply the conversion.

This became increasingly awkward as the `Matricks` class grew more complex.  Consequently,
the conversion director was created.  This provides a way to specify individual
column conversion, thereby permitting mixed conversions on a per-column basis.
The old semantics will still work and are used to create a conversion director
that mimics the older behaviour.

Conversion Specifiers
---------------------

Conversion can be specified one of several ways::

 *function* + *skipcols* :
   this mimics the older behaviour.  If a function is provided to the constructer it will 
   be applied to all columns beyond the first `skipcols` colunmns.  The `skipcols` argument
   can be provided to override the default of 1.

 *string* :
   a string of single-character format specifiers can be provided that will be used to 
   construct the list of conversion functions, not unlike the format controls used in
   a "C"-style printf format.

    s: string
    i: integer
    x: hexadecimal
    o: octal
    b: boolean
    f: float
    n: numeric
    -: no conversion
    *: ignore/omit this column

 *sequence*:
  this should be a sequence (list or tuple) of functions that correspond, positionlly
  with the columns they'll be used to convert.

 *dict*:
  a dictionary that associates column label names with functions that will do the conversion.


 >>> cd = ConversionDirector(float)
 >>> print cd(['1', '2', '3', '4', '5.6', '-7.8', '-9', '0.01e10'])

 >>> cd = ConversionDirector(float, 2)
 >>> print cd(['1', '2', '3', '4', '5.6', '-7.8', '-9', '0.01e10'])

 
"""

from types import FunctionType, TypeType

class ConversionDirector(object):

    @staticmethod
    def _cvt_numeric(v):
        try:
            cv = float(v)
        except ValueError:
            cv = int(v)
        return cv
    
    _conversion_control_map = {
        's': str,
        'i': int,
        'x': lambda x: int (x, 16),
        'o' :lambda o: int (o, 8),
        'b': lambda q: isinstance(q, (str, unicode)) and q.upper()[0] == 'T',
        'f': float,
        'n': _cvt_numeric,   # might need a bit of work, here.
        '-': lambda x: x,
        '*': lambda x: None,
        }

       
    def __init__(self, prog, skipcols=0):

        if not isinstance(skipcols, int) or (skipcols < 0):
            raise ValueError('skipcols must be an int >= 0')
        self.__skipcols = skipcols

        self.__defaultCvt = lambda x: x
        
        if isinstance(prog, (type, FunctionType)):
            self.__converterDict = {-1: prog}
            self.__defaultCvt = prog
        
        elif isinstance(prog, (list, tuple)):
            self._converterDict = dict(zip(range(len(prog)), prog))

        elif isinstance(prog, dict):
            self._converterDict = dict()
            for k,v in prog.items():
                if isinstance(k, int):
                    self._converterDict[k] = v
                elif isinstance(k, (string, unicode)):
                    if self._label_map.has_key(k):
                        self._converterDict[self._label_map[k]] = v

        elif isinstance(prog, (string, unicode)):
            self._converterDict = dict()
            for i in range(len(prog)):
                cf = self._conversion_control_map.get(prog[i], self.__defaultCvt)  # default is no conversion
                self._converterDict[i] = cf

                                       
    def __getitem__(self, key):
        return self.__converterDict.get(key, self.__defaultConv)


    def __call__(self, seq):
        return seq[:self.__skipcols] + [ self.__converterDict.get(i, self.__defaultCvt)(seq[i]) for i in range(self.__skipcols,len(seq)) ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
        
                    
