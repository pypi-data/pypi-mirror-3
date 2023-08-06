"""
MATRICKS: Manipulate Datasets as Matrices
=========================================

Class for importing and querying expression dataasets organized as a column-
and row-annotated  matrix.

.. include:: <isolat1.txt>

.. |godel| unicode:: G U+000F6 del

Expression datasets contain the numeric results of one or more samples
derived from microarray assays.   Common to each of the assays is the
specific platform (microarray).   The dataset can be regarded as a table
with rows and columns.  Each column represents a single assay, and each row 
contains the assay results for a specific probe on the assay platform.  Thus,
the values in any given row are those obtained from the same probe location
on the platform.  These are referred to as `expression profiles`.

A dataset can be regarded as a table, such as this one (excerpted from
the `Goodell dataset`_):

+----------+-------+-------+-------+-------+
| probe_id | HSC 1 | HSC 2 | NK 1  | NK 2  | 
+==========+=======+=======+=======+=======+
| 45283    | 10.14 |  9.31 |   8.9 |  8.78 |
+----------+-------+-------+-------+-------+
| 45284    | 12.52 | 12.63 | 12.55 | 11.96 |
+----------+-------+-------+-------+-------+
| 45285    |  6.78 |  6.91 |  7.83 |  7.86 |
+----------+-------+-------+-------+-------+
| 45286    |  5.58 |  5.06 |  6.69 |  6.64 |
+----------+-------+-------+-------+-------+
| 45287    |  7.85 |  8.13 |  8.47 |  8.56 |
+----------+-------+-------+-------+-------+
| 45288    |  8.12 |  7.17 |  8.71 |  8.08 |
+----------+-------+-------+-------+-------+
| 45289    |  6.82 |  6.15 |  5.87 |  5.32 |
+----------+-------+-------+-------+-------+
| 45290    | 10.55 | 10.39 |  10.7 |  9.93 |
+----------+-------+-------+-------+-------+


.. _Goodell dataset: http://www.bcm.edu/db/db_fac-goodell.html

Expression datasets, with rare exception, are stored in text (i.e. flat) files
that have the following format:

* two or more rows of data, delimited by ASCII newline (\\x0a) characters.
  (Strictly speaking, there needen't be any data at all, but what's the point of that?)

* each line or row consists of two or more columns of data, delimited by ASCII TAB (\\x09) characters.

* the first column contains the key or `probe ID`, assumed to be alpha-numeric, or for the probe.

* the first row consists of labels identifying the probe ID and sample columns.  This, too, is assumed
  to be alpha-numeric.

* the second through last rows contain expression values and, aside from the first column, which
  contains the probe ID, are assumed to be floating point numbers.  In microarray parlance, 
  each row is  typically referred to as an `expression profile`.

Some datasets may differ from this format.  For instance, there may be no (first) row of labels,
or the data may be of some format other than floating point.  Provision is made for handling these
arguably special cases.  However, the default settings for instantiating `Matricks` classes
makes the foregoing assumptions about the contents of raw source data.  It is further assumed that
the source dataset is encoded in ASCII strings, requiring the conversion of all numeric data
to ``float`` type objects.

`Matricks` selection operations generally return `Matricks` objects.   These can be iterated,
row-wise, much like lists or tuples, to access individual expression profiles, the contents of which
can be retrieved using list / tuple semantics.

Instantiating a Matricks
------------------------

If no source dataset is supplied at instantiation, a `Matricks` is empty or null.  This isn't terribly useful
and operations on it will almost always return ``None`` or raise a `MatricksError` exception.


 >>> # Create an empty Matricks instance.
 >>> a0 = Matricks()
 >>> print a0
    [[ ... ]]

A `Matricks` can be loaded with data either by providing a source at instantiation, or by using the
``load`` method.  (Internally, the instantiation approach just calls ``load``.)  The source can be
a string, a file (or file-like) object, a list or tuple, or another `Matricks` instance.  

We'll use a small, representative dataset that is nothing more than a list of lists.  

 >>> test_raw_data = [\
 ['probe_id','ABC(12)','ABC(13)','DEFC0N(1)','CDDB4(5)','Jovi(1)','F774Lin(3)'],
 ... ['ELMT_3401602','7.14727114229','1.682159','6.6022379846','6.6318799406','6.63021747852','6.57620493019'],
 ... ['ELMT_3401603','6.6469632681','1.682159','6.63635120703','6.70026291599','6.67341553263','6.66361340118'],
 ... ['ELMT_3401605','9.33488740366','1.682159','9.7365656865','8.88887581915','8.70271863949','9.39432724993'],
 ... ['ELMT_3401607','6.65137398038','1.682159','6.75639196465','6.70203184527','7.05207191931','6.96818993978'],
 ... ['ELMT_3401612','6.58374160839','1.682159','7.05322172216','6.62893626542','6.51635952774','6.66963293585'],
 ... ['ELMT_3401614','6.59679034883','1.682159','6.65934616753','6.54032931162','6.5067348291','6.53686489577'],
 ... ['ELMT_3401619','6.66351268706','1.682159','6.67986657646','6.57837221187','6.78383553317','7.26045576436'],
 ... ['ELMT_3401623','6.65611759304','1.682159','6.80554955104','6.64764879202','6.6403692878','6.67254761381'],
 ... ['ELMT_3401625','10.6488388784','1.682159','10.3501936853','9.26241934526','9.84545402073','10.0755468901'],
 ... ['ELMT_3401626','7.5310613409','1.682159','8.10062767869','9.24637465474','11.2541801046','7.11119485886'],
 ... ['ELMT_3401628','6.55860431817','1.682159','6.63538974978','6.66347280086','6.68541200426','6.53825496578'],
 ... ['ELMT_3401632','6.97318937509','1.682159','6.59048802252','6.68431036403','6.67796164216','7.47303945599'],
 ... ['ELMT_3401633','7.20203718782','1.682159','7.33123060039','6.93376501527','7.40407740412','8.28373011066'],
 ... ['ELMT_3401636','11.4847211865','1.682159','11.7592497692','10.8845553078','10.7344737293','12.3247525578'],
 ... ['ELMT_3401637','9.15673736606','1.682159','9.93949907204','8.84061428541','9.69594817225','10.7308783293'],
 ... ['ELMT_3401638','0','1.682159','0','13.4536343874','13.5199773001','13.4779333646'],
 ... ['ELMT_3401639','7.23211276845','1.682159','6.95198458669','6.96898611023','6.68270691586','6.69342317943'],
 ... ['Elmt_3401639','7.23211276845','1.682159','6.95198458669','6.96898611023','6.68270691586','6.69342317943'],
 ... ['ELMT_3401644','6.66459889061','1.682159','6.65469610536','6.59303032509','6.63139625302','6.72401222705'],
 ... ['ELMT_3401645','9.48762418312','1.682159','8.8286277291','7.66907923624','8.4171269045','6.65231345481'],
 ...  ]

In fact, let's re-write this to look like TSV input::

 >>> test_raw_data = '''\
 probe_id\\tABC(12)\\tABC(13)\\tDEFC0N(1)\\tCDDB4(5)\\tJovi(1)\\tF774Lin(3)
 ... ELMT_3401602\\t7.14727114229\\t1.682159\\t6.6022379846\\t6.6318799406\\t6.63021747852\\t6.57620493019
 ... ELMT_3401603\\t6.6469632681\\t1.682159\\t6.63635120703\\t6.70026291599\\t6.67341553263\\t6.66361340118
 ... ELMT_3401605\\t9.33488740366\\t1.682159\\t9.7365656865\\t8.88887581915\\t8.70271863949\\t9.39432724993
 ... ELMT_3401607\\t6.65137398038\\t1.682159\\t6.75639196465\\t6.70203184527\\t7.05207191931\\t6.96818993978
 ... ELMT_3401612\\t6.58374160839\\t1.682159\\t7.05322172216\\t6.62893626542\\t6.51635952774\\t6.66963293585
 ... ELMT_3401614\\t6.59679034883\\t1.682159\\t6.65934616753\\t6.54032931162\\t6.5067348291\\t6.53686489577
 ... ELMT_3401619\\t6.66351268706\\t1.682159\\t6.67986657646\\t6.57837221187\\t6.78383553317\\t7.26045576436
 ... ELMT_3401623\\t6.65611759304\\t1.682159\\t6.80554955104\\t6.64764879202\\t6.6403692878\\t6.67254761381
 ... ELMT_3401625\\t10.6488388784\\t1.682159\\t10.3501936853\\t9.26241934526\\t9.84545402073\\t10.0755468901
 ... ELMT_3401626\\t7.5310613409\\t1.682159\\t8.10062767869\\t9.24637465474\\t11.2541801046\\t7.11119485886
 ... ELMT_3401628\\t6.55860431817\\t1.682159\\t6.63538974978\\t6.66347280086\\t6.68541200426\\t6.53825496578
 ... ELMT_3401632\\t6.97318937509\\t1.682159\\t6.59048802252\\t6.68431036403\\t6.67796164216\\t7.47303945599
 ... ELMT_3401633\\t7.20203718782\\t1.682159\\t7.33123060039\\t6.93376501527\\t7.40407740412\\t8.28373011066
 ... ELMT_3401636\\t11.4847211865\\t1.682159\\t11.7592497692\\t10.8845553078\\t10.7344737293\\t12.3247525578
 ... ELMT_3401637\\t9.15673736606\\t1.682159\\t9.93949907204\\t8.84061428541\\t9.69594817225\\t10.7308783293
 ... ELMT_3401638\\t0\\t1.682159\\t0\\t13.4536343874\\t13.5199773001\\t13.4779333646
 ... ELMT_3401639\\t7.23211276845\\t1.682159\\t6.95198458669\\t6.96898611023\\t6.68270691586\\t6.69342317943
 ... Elmt_3401639\\t7.23211276845\\t1.682159\\t6.95198458669\\t6.96898611023\\t6.68270691586\\t6.69342317943
 ... ELMT_3401644\\t6.66459889061\\t1.682159\\t6.65469610536\\t6.59303032509\\t6.63139625302\\t6.72401222705
 ... ELMT_3401645\\t9.48762418312\\t1.682159\\t8.8286277291\\t7.66907923624\\t8.4171269045\\t6.65231345481'''
 

We then create the instance that will hold this dataset::

 >>> a_pre1 = Matricks(test_raw_data, cvt=float)

Notice that we specified ``cvt=float``. Elements that are in rows before the first row and to the right of
the first column will be converted to type ``float`` using the float constructor.  We can use more elaborate
functions to do this conversion, but this will do for now.  Also note that because the file is otherwise in
TSV format, we didn't have to specify any additional arguments.   If it were comma-separated (CSV rather than
TSV, instance creation would look like this:

 >>> test_raw_data_csv = '''\
 probe_id,ABC(12),ABC(13),DEFC0N(1),CDDB4(5),Jovi(1),F774Lin(3)
 ... ELMT_3401602,7.14727114229,1.682159,6.6022379846,6.6318799406,6.63021747852,6.57620493019
 ... ELMT_3401603,6.6469632681,1.682159,6.63635120703,6.70026291599,6.67341553263,6.66361340118
 ... ELMT_3401605,9.33488740366,1.682159,9.7365656865,8.88887581915,8.70271863949,9.39432724993
 ... ELMT_3401607,6.65137398038,1.682159,6.75639196465,6.70203184527,7.05207191931,6.96818993978
 ... ELMT_3401612,6.58374160839,1.682159,7.05322172216,6.62893626542,6.51635952774,6.66963293585
 ... ELMT_3401614,6.59679034883,1.682159,6.65934616753,6.54032931162,6.5067348291,6.53686489577
 ... ELMT_3401619,6.66351268706,1.682159,6.67986657646,6.57837221187,6.78383553317,7.26045576436
 ... ELMT_3401623,6.65611759304,1.682159,6.80554955104,6.64764879202,6.6403692878,6.67254761381
 ... ELMT_3401625,10.6488388784,1.682159,10.3501936853,9.26241934526,9.84545402073,10.0755468901
 ... ELMT_3401626,7.5310613409,1.682159,8.10062767869,9.24637465474,11.2541801046,7.11119485886
 ... ELMT_3401628,6.55860431817,1.682159,6.63538974978,6.66347280086,6.68541200426,6.53825496578
 ... ELMT_3401632,6.97318937509,1.682159,6.59048802252,6.68431036403,6.67796164216,7.47303945599
 ... ELMT_3401633,7.20203718782,1.682159,7.33123060039,6.93376501527,7.40407740412,8.28373011066
 ... ELMT_3401636,11.4847211865,1.682159,11.7592497692,10.8845553078,10.7344737293,12.3247525578
 ... ELMT_3401637,9.15673736606,1.682159,9.93949907204,8.84061428541,9.69594817225,10.7308783293
 ... ELMT_3401638,0,1.682159,0,13.4536343874,13.5199773001,13.4779333646
 ... ELMT_3401639,7.23211276845,1.682159,6.95198458669,6.96898611023,6.68270691586,6.69342317943
 ... Elmt_3401639,7.23211276845,1.682159,6.95198458669,6.96898611023,6.68270691586,6.69342317943
 ... ELMT_3401644,6.66459889061,1.682159,6.65469610536,6.59303032509,6.63139625302,6.72401222705
 ... ELMT_3401645,9.48762418312,1.682159,8.8286277291,7.66907923624,8.4171269045,6.65231345481'''
 
 >>> a_pre1_csv = Matricks(test_raw_data_csv, fsep=',', cvt=float)
 
We can see an abridged depiction of these by using ``print``::

 >>> print a_pre1
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401602' 7.14727114229 1.682159 ... 6.6318799406 6.63021747852 6.57620493019],
      ['ELMT_3401603' 6.6469632681 1.682159 ... 6.70026291599 6.67341553263 6.66361340118],
      ['ELMT_3401605' 9.33488740366 1.682159 ... 8.88887581915 8.70271863949 9.39432724993],
    ...  
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['ELMT_3401644' 6.66459889061 1.682159 ... 6.59303032509 6.63139625302 6.72401222705],
      ['ELMT_3401645' 9.48762418312 1.682159 ... 7.66907923624 8.4171269045 6.65231345481]]

 >>> print a_pre1_csv
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401602' 7.14727114229 1.682159 ... 6.6318799406 6.63021747852 6.57620493019],
      ['ELMT_3401603' 6.6469632681 1.682159 ... 6.70026291599 6.67341553263 6.66361340118],
      ['ELMT_3401605' 9.33488740366 1.682159 ... 8.88887581915 8.70271863949 9.39432724993],
    ...  
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['ELMT_3401644' 6.66459889061 1.682159 ... 6.59303032509 6.63139625302 6.72401222705],
      ['ELMT_3401645' 9.48762418312 1.682159 ... 7.66907923624 8.4171269045 6.65231345481]]

Call ``getLabels`` to see the columns labels.

 >>> print a_pre1.getLabels()
    ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']

We can specify which labels we want, either by their index::

 >>> print a_pre1.getLabels(3, 6, 0)
   ['DEFC0N(1)', 'F774Lin(3)', 'probe_id']

or we can use a string or regular expression::

 >>> print a_pre1.getLabels('ABC(12)', 'CDDB4.*', '.*\(1)', re=True)
    ['ABC(12)', ['CDDB4(5)'], ['DEFC0N(1)', 'Jovi(1)']]


We could have also specified a string for the data source, which would have been
used to open a file or remote URL (internally, urllib is used in either case), or we
could have specified a file-like object (from the built-in ``open`` function 
or an explicit ``urllib.urlopen`` that we did ourselves prior to
instantiating a `Matricks`.  These are difficult to test using doctest, though,
so we'll leave those for another test scenario.  

The last way we can populate an instance is with another instance::

 >>> a1 = Matricks(a_pre1)
 >>> print a1.getLabels()
    ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']

 >>> for r in a1: print r
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978]
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585]
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577]
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436]
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381]
    ['ELMT_3401625', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901]
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886]
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066]
    ['ELMT_3401636', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578]
    ['ELMT_3401637', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293]
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646]
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705]
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481]

Let's check to make sure they're equal::

 >>> print False not in [ t[0] == t[1] for t in zip(a_pre1, a1 ) ]
    True

Note again that, since the ``zip`` built-in function expects iterable objects, it treats
the two `Matricks` instances as though they were.  This works in most, if not all other cases
that handle iterables.

Writing Data:  Files
--------------------

Data can be exported from a `Matricks` instance a couple of different ways.  The
`dumps` method  converts the labels and data into one (possibly very long) string
in a format that can be (re)loaded using the `load` method without any non-default options.   As such, it
essentially writes a TAB-separated version (TSV) of the data that can be written as-is to a file or 
stream.  
Here's an example of how to use the `dumps` method::

 >>> a1_s = a1.dumps()
 >>> print a1_s
    probe_id	ABC(12)	ABC(13)	DEFC0N(1)	CDDB4(5)	Jovi(1)	F774Lin(3)
    ELMT_3401602	7.14727114229	1.682159	6.6022379846	6.6318799406	6.63021747852	6.57620493019
    ELMT_3401603	6.6469632681	1.682159	6.63635120703	6.70026291599	6.67341553263	6.66361340118
    ELMT_3401605	9.33488740366	1.682159	9.7365656865	8.88887581915	8.70271863949	9.39432724993
    ELMT_3401607	6.65137398038	1.682159	6.75639196465	6.70203184527	7.05207191931	6.96818993978
    ELMT_3401612	6.58374160839	1.682159	7.05322172216	6.62893626542	6.51635952774	6.66963293585
    ELMT_3401614	6.59679034883	1.682159	6.65934616753	6.54032931162	6.5067348291	6.53686489577
    ELMT_3401619	6.66351268706	1.682159	6.67986657646	6.57837221187	6.78383553317	7.26045576436
    ELMT_3401623	6.65611759304	1.682159	6.80554955104	6.64764879202	6.6403692878	6.67254761381
    ELMT_3401625	10.6488388784	1.682159	10.3501936853	9.26241934526	9.84545402073	10.0755468901
    ELMT_3401626	7.5310613409	1.682159	8.10062767869	9.24637465474	11.2541801046	7.11119485886
    ELMT_3401628	6.55860431817	1.682159	6.63538974978	6.66347280086	6.68541200426	6.53825496578
    ELMT_3401632	6.97318937509	1.682159	6.59048802252	6.68431036403	6.67796164216	7.47303945599
    ELMT_3401633	7.20203718782	1.682159	7.33123060039	6.93376501527	7.40407740412	8.28373011066
    ELMT_3401636	11.4847211865	1.682159	11.7592497692	10.8845553078	10.7344737293	12.3247525578
    ELMT_3401637	9.15673736606	1.682159	9.93949907204	8.84061428541	9.69594817225	10.7308783293
    ELMT_3401638	0.0	1.682159	0.0	13.4536343874	13.5199773001	13.4779333646
    ELMT_3401639	7.23211276845	1.682159	6.95198458669	6.96898611023	6.68270691586	6.69342317943
    Elmt_3401639	7.23211276845	1.682159	6.95198458669	6.96898611023	6.68270691586	6.69342317943
    ELMT_3401644	6.66459889061	1.682159	6.65469610536	6.59303032509	6.63139625302	6.72401222705
    ELMT_3401645	9.48762418312	1.682159	8.8286277291	7.66907923624	8.4171269045	6.65231345481

The contents of a `Matricks` can be written to a file using the
`dump` or `dumps` methods.   The latter creates a string-enggded version of
the instance that can, if read from a file, be ingested by `load` with no other
option changes (i.e., *fsep* and *rsep* defaults will work.)  The `dump` method
just writes the output of `dumps` to the specified file or file-like object::

 >>> import os
 >>> try:
 ...     os.unlink('/tmp/matricks_doctest.tsv')  # in case left over from earlier run
 ... except:
 ...     pass
 
 >>> print a1.dump('/tmp/matricks_doctest.tsv')
     1873
 
We can read this into another `Matricks`::

 >>> a1reloaded = Matricks('/tmp/matricks_doctest.tsv', cvt=float)

And, again, see that they're equal::

 >>> print False not in [ t[0] == t[1] for t in zip(a1, a1reloaded) ]
    True

(Clean up after ourselves.)::

 >>> os.unlink('/tmp/matricks_doctest.tsv') 

Pickling
,,,,,,,,

`Matricks` instances can be pickled::

 >>> import cPickle
 >>> a1_save = cPickle.dumps(a1, -1)   # Use highest protocol

and unpickled::

 >>> a1_restored = cPickle.loads(a1_save)
 >>> print type(a1_restored)
    <class '__main__.Matricks'>
 >>> print a1_restored
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401602' 7.14727114229 1.682159 ... 6.6318799406 6.63021747852 6.57620493019],
      ['ELMT_3401603' 6.6469632681 1.682159 ... 6.70026291599 6.67341553263 6.66361340118],
      ['ELMT_3401605' 9.33488740366 1.682159 ... 8.88887581915 8.70271863949 9.39432724993],
    ...  
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['ELMT_3401644' 6.66459889061 1.682159 ... 6.59303032509 6.63139625302 6.72401222705],
      ['ELMT_3401645' 9.48762418312 1.682159 ... 7.66907923624 8.4171269045 6.65231345481]]


Pickling and unpickling is a much faster way to store and retrieve `Matricks`
instances, and using the higher pickle protocols provides the fastest speeds since
they use binary formats, which are closer to the internal encodings.  
In fact, if a string or a file-like object is passed to the constructor (or the `load` method)
for the input source, an attempt is first made to unpickle whatever's read in.  If this fails, the
input is otherwise split and parsed.

 >>> cx = cPickle.dump(a1, open('/tmp/a1.P', 'w'), -1)
 >>> cy = Matricks(open('/tmp/a1.P', 'r'))
 >>> print False not in [ t[0] == t[1] for t in zip(a1, cy ) ]
    True
 >>> os.unlink('/tmp/a1.P')

**Caveat**: since functions cannot be pickled, the default aggregator function
will be set to ``Matricks.arithmetic_mean`` when an instance is unpickled.  If some other
function had been specified when the instance was originally constructed, it will have to be
explicitly reset to this after unpickling.

JSON
,,,,

A convenience method -- ``json`` -- is provided that will return a simple rendition into
string (JSON) format of the labels and data contained within a `Matricks` instance.

 >>> ja1 = a1.json()
 >>> print ja1
    [["probe_id", "ABC(12)", "ABC(13)", "DEFC0N(1)", "CDDB4(5)", "Jovi(1)", "F774Lin(3)"], ["ELMT_3401602", 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019], ["ELMT_3401603", 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118], ["ELMT_3401605", 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993], ["ELMT_3401607", 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978], ["ELMT_3401612", 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585], ["ELMT_3401614", 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577], ["ELMT_3401619", 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436], ["ELMT_3401623", 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381], ["ELMT_3401625", 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901], ["ELMT_3401626", 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886], ["ELMT_3401628", 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578], ["ELMT_3401632", 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599], ["ELMT_3401633", 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066], ["ELMT_3401636", 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578], ["ELMT_3401637", 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293], ["ELMT_3401638", 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646], ["ELMT_3401639", 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943], ["Elmt_3401639", 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943], ["ELMT_3401644", 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705], ["ELMT_3401645", 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481]]

GCT
,,,


GCT format is also supported.  Supply a file-like object to this method and it will
write the `Matricks` instance out in GCT-compatible format.  Note that some fields are 
"guessed" at (second row, `Description` column, `Accession` column.)

Example:


..code-block:: python

 >>> import sys
 >>> from cStringIO import StringIO
 >>> outf = StringIO()
 >>> a1.gct(outf)
 >>> print outf.getvalue()
    #1.2
    20	6
    NAME	Description	ABC(12)	ABC(13)	DEFC0N(1)	CDDB4(5)	Jovi(1)	F774Lin(3)
    ELMT_3401602	na	7.14727114229	1.682159	6.6022379846	6.6318799406	6.63021747852	6.57620493019
    ELMT_3401603	na	6.6469632681	1.682159	6.63635120703	6.70026291599	6.67341553263	6.66361340118
    ELMT_3401605	na	9.33488740366	1.682159	9.7365656865	8.88887581915	8.70271863949	9.39432724993
    ELMT_3401607	na	6.65137398038	1.682159	6.75639196465	6.70203184527	7.05207191931	6.96818993978
    ELMT_3401612	na	6.58374160839	1.682159	7.05322172216	6.62893626542	6.51635952774	6.66963293585
    ELMT_3401614	na	6.59679034883	1.682159	6.65934616753	6.54032931162	6.5067348291	6.53686489577
    ELMT_3401619	na	6.66351268706	1.682159	6.67986657646	6.57837221187	6.78383553317	7.26045576436
    ELMT_3401623	na	6.65611759304	1.682159	6.80554955104	6.64764879202	6.6403692878	6.67254761381
    ELMT_3401625	na	10.6488388784	1.682159	10.3501936853	9.26241934526	9.84545402073	10.0755468901
    ELMT_3401626	na	7.5310613409	1.682159	8.10062767869	9.24637465474	11.2541801046	7.11119485886
    ELMT_3401628	na	6.55860431817	1.682159	6.63538974978	6.66347280086	6.68541200426	6.53825496578
    ELMT_3401632	na	6.97318937509	1.682159	6.59048802252	6.68431036403	6.67796164216	7.47303945599
    ELMT_3401633	na	7.20203718782	1.682159	7.33123060039	6.93376501527	7.40407740412	8.28373011066
    ELMT_3401636	na	11.4847211865	1.682159	11.7592497692	10.8845553078	10.7344737293	12.3247525578
    ELMT_3401637	na	9.15673736606	1.682159	9.93949907204	8.84061428541	9.69594817225	10.7308783293
    ELMT_3401638	na	0.0	1.682159	0.0	13.4536343874	13.5199773001	13.4779333646
    ELMT_3401639	na	7.23211276845	1.682159	6.95198458669	6.96898611023	6.68270691586	6.69342317943
    Elmt_3401639	na	7.23211276845	1.682159	6.95198458669	6.96898611023	6.68270691586	6.69342317943
    ELMT_3401644	na	6.66459889061	1.682159	6.65469610536	6.59303032509	6.63139625302	6.72401222705
    ELMT_3401645	na	9.48762418312	1.682159	8.8286277291	7.66907923624	8.4171269045	6.65231345481

 >>> a1gct = Matricks(outf.getvalue())
 >>> print a1gct.labels
    ['NAME', 'Description', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']

 >>> for r in a1gct: print r
    ['ELMT_3401602', 'na', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019]
    ['ELMT_3401603', 'na', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118]
    ['ELMT_3401605', 'na', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]
    ['ELMT_3401607', 'na', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978]
    ['ELMT_3401612', 'na', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585]
    ['ELMT_3401614', 'na', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577]
    ['ELMT_3401619', 'na', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436]
    ['ELMT_3401623', 'na', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381]
    ['ELMT_3401625', 'na', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901]
    ['ELMT_3401626', 'na', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886]
    ['ELMT_3401628', 'na', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401632', 'na', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599]
    ['ELMT_3401633', 'na', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066]
    ['ELMT_3401636', 'na', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578]
    ['ELMT_3401637', 'na', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293]
    ['ELMT_3401638', 'na', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646]
    ['ELMT_3401639', 'na', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 'na', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['ELMT_3401644', 'na', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705]
    ['ELMT_3401645', 'na', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481]


DataTables
,,,,,,,,,,

Support for `DataTables`_
server-side processing
is provided with the `dataTablesObject` method.  Invoking this will return
a dictionary that has ``aaData``, ``aoColumns``, ``iTotalRecords``, and ``sColumns``
elements set in a way that is readily digestible by `DataTables`.  This can be called
with ``offset=`` and ``limit=`` keyword arguments to further support server-side 
pagination through large datasets.

.. _DataTables: http://www.datatables.net/

Retrieving Matricks Contents: Column Labels 
-------------------------------------------

We've already seen that we can retrieve the column labels (alternatively called
*sample names* or *sample labels*: iteration, and the `getLabels` method.

Take another look at what `getLabels` returned, above, and you'll notice
that in the pattern example it's a list of sublists.
This happens when a regular expression
is expanded, or when a sublist of explicity strings (or indexes) has been
supplied as input to `getlabels`.  If the ``flat=`` keyword argument is
set to ``True``, the result will be `flattened` into a single, unstructured list:: 

 >>> print a_pre1.getLabels('ABC(12)', 'CDDB4.*', '.*\(1)', flat=True, re=True)
   ['ABC(12)', 'CDDB4(5)', 'DEFC0N(1)', 'Jovi(1)']

If we want the complement of this set, we can set ``cmpl=True`` in the
keyword arguments::

 >>> print a_pre1.getLabels('ABC.*', cmpl=True, re=True)
    [['probe_id', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']]

Retrieving Matricks Contents: Data
----------------------------------

We looked at our example dataset earlier by simply iterating through it just as we would
any list of objects. 
`Matricks` instances can be used like any other iterable type (lists, tuples, etc.) with
each iteration returning the next expression profile (row) in the data set. 

 >>> print len(a1) == 20 and len(a1) == len([ x for x in a1 ])
    True
 >>> print len(a0)
    0

Each iteration of a `Matricks` returns a python 
`list` object by default, the elements therein being associated with
their respective samples by having the same index within the list as the sample's label in the label
list (see `getLabels` method.)   A convenience function is provided that will return a dictionary
associating the elements associated with their corresponding sample labels::

 >>> for r in a1: print a1.todict(r)
    OrderedDict([('probe_id', 'ELMT_3401602'), ('ABC(12)', 7.14727114229), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.6022379846), ('CDDB4(5)', 6.6318799406), ('Jovi(1)', 6.63021747852), ('F774Lin(3)', 6.57620493019)])
    OrderedDict([('probe_id', 'ELMT_3401603'), ('ABC(12)', 6.6469632681), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.63635120703), ('CDDB4(5)', 6.70026291599), ('Jovi(1)', 6.67341553263), ('F774Lin(3)', 6.66361340118)])
    OrderedDict([('probe_id', 'ELMT_3401605'), ('ABC(12)', 9.33488740366), ('ABC(13)', 1.682159), ('DEFC0N(1)', 9.7365656865), ('CDDB4(5)', 8.88887581915), ('Jovi(1)', 8.70271863949), ('F774Lin(3)', 9.39432724993)])
    OrderedDict([('probe_id', 'ELMT_3401607'), ('ABC(12)', 6.65137398038), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.75639196465), ('CDDB4(5)', 6.70203184527), ('Jovi(1)', 7.05207191931), ('F774Lin(3)', 6.96818993978)])
    OrderedDict([('probe_id', 'ELMT_3401612'), ('ABC(12)', 6.58374160839), ('ABC(13)', 1.682159), ('DEFC0N(1)', 7.05322172216), ('CDDB4(5)', 6.62893626542), ('Jovi(1)', 6.51635952774), ('F774Lin(3)', 6.66963293585)])
    OrderedDict([('probe_id', 'ELMT_3401614'), ('ABC(12)', 6.59679034883), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.65934616753), ('CDDB4(5)', 6.54032931162), ('Jovi(1)', 6.5067348291), ('F774Lin(3)', 6.53686489577)])
    OrderedDict([('probe_id', 'ELMT_3401619'), ('ABC(12)', 6.66351268706), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.67986657646), ('CDDB4(5)', 6.57837221187), ('Jovi(1)', 6.78383553317), ('F774Lin(3)', 7.26045576436)])
    OrderedDict([('probe_id', 'ELMT_3401623'), ('ABC(12)', 6.65611759304), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.80554955104), ('CDDB4(5)', 6.64764879202), ('Jovi(1)', 6.6403692878), ('F774Lin(3)', 6.67254761381)])
    OrderedDict([('probe_id', 'ELMT_3401625'), ('ABC(12)', 10.6488388784), ('ABC(13)', 1.682159), ('DEFC0N(1)', 10.3501936853), ('CDDB4(5)', 9.26241934526), ('Jovi(1)', 9.84545402073), ('F774Lin(3)', 10.0755468901)])
    OrderedDict([('probe_id', 'ELMT_3401626'), ('ABC(12)', 7.5310613409), ('ABC(13)', 1.682159), ('DEFC0N(1)', 8.10062767869), ('CDDB4(5)', 9.24637465474), ('Jovi(1)', 11.2541801046), ('F774Lin(3)', 7.11119485886)])
    OrderedDict([('probe_id', 'ELMT_3401628'), ('ABC(12)', 6.55860431817), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.63538974978), ('CDDB4(5)', 6.66347280086), ('Jovi(1)', 6.68541200426), ('F774Lin(3)', 6.53825496578)])
    OrderedDict([('probe_id', 'ELMT_3401632'), ('ABC(12)', 6.97318937509), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.59048802252), ('CDDB4(5)', 6.68431036403), ('Jovi(1)', 6.67796164216), ('F774Lin(3)', 7.47303945599)])
    OrderedDict([('probe_id', 'ELMT_3401633'), ('ABC(12)', 7.20203718782), ('ABC(13)', 1.682159), ('DEFC0N(1)', 7.33123060039), ('CDDB4(5)', 6.93376501527), ('Jovi(1)', 7.40407740412), ('F774Lin(3)', 8.28373011066)])
    OrderedDict([('probe_id', 'ELMT_3401636'), ('ABC(12)', 11.4847211865), ('ABC(13)', 1.682159), ('DEFC0N(1)', 11.7592497692), ('CDDB4(5)', 10.8845553078), ('Jovi(1)', 10.7344737293), ('F774Lin(3)', 12.3247525578)])
    OrderedDict([('probe_id', 'ELMT_3401637'), ('ABC(12)', 9.15673736606), ('ABC(13)', 1.682159), ('DEFC0N(1)', 9.93949907204), ('CDDB4(5)', 8.84061428541), ('Jovi(1)', 9.69594817225), ('F774Lin(3)', 10.7308783293)])
    OrderedDict([('probe_id', 'ELMT_3401638'), ('ABC(12)', 0.0), ('ABC(13)', 1.682159), ('DEFC0N(1)', 0.0), ('CDDB4(5)', 13.4536343874), ('Jovi(1)', 13.5199773001), ('F774Lin(3)', 13.4779333646)])
    OrderedDict([('probe_id', 'ELMT_3401639'), ('ABC(12)', 7.23211276845), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.95198458669), ('CDDB4(5)', 6.96898611023), ('Jovi(1)', 6.68270691586), ('F774Lin(3)', 6.69342317943)])
    OrderedDict([('probe_id', 'Elmt_3401639'), ('ABC(12)', 7.23211276845), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.95198458669), ('CDDB4(5)', 6.96898611023), ('Jovi(1)', 6.68270691586), ('F774Lin(3)', 6.69342317943)])
    OrderedDict([('probe_id', 'ELMT_3401644'), ('ABC(12)', 6.66459889061), ('ABC(13)', 1.682159), ('DEFC0N(1)', 6.65469610536), ('CDDB4(5)', 6.59303032509), ('Jovi(1)', 6.63139625302), ('F774Lin(3)', 6.72401222705)])
    OrderedDict([('probe_id', 'ELMT_3401645'), ('ABC(12)', 9.48762418312), ('ABC(13)', 1.682159), ('DEFC0N(1)', 8.8286277291), ('CDDB4(5)', 7.66907923624), ('Jovi(1)', 8.4171269045), ('F774Lin(3)', 6.65231345481)])


Matricks Attributes
-------------------
`Matrickss` have several, read-only attributes and properties::

 *length* : (int)
  number of rows of data, not including the label row(s).

 *min* : (float)
  numeric minimum of all the values in the `Matricks` instance.

 *max* : (float)
  numeric maximum of all the values in the `Matricks` instance.

 *mean* : (float)
  arithmetic mean of all the values in the `Matricks` instance.


Selecting subsets
-----------------

Suppose we are interested in just one of the samples contained in this set.  We can extract this, 
creating another, separate `Matricks` instance, using python's *slice* semantics:

 >>> r1 = a1['probe_id', 'DEFC0N(1)']
 >>> print r1.getLabels()
    ['probe_id', 'DEFC0N(1)']

 >>> for r in r1: print r
    ['ELMT_3401602', 6.6022379846]
    ['ELMT_3401603', 6.63635120703]
    ['ELMT_3401605', 9.7365656865]
    ['ELMT_3401607', 6.75639196465]
    ['ELMT_3401612', 7.05322172216]
    ['ELMT_3401614', 6.65934616753]
    ['ELMT_3401619', 6.67986657646]
    ['ELMT_3401623', 6.80554955104]
    ['ELMT_3401625', 10.3501936853]
    ['ELMT_3401626', 8.10062767869]
    ['ELMT_3401628', 6.63538974978]
    ['ELMT_3401632', 6.59048802252]
    ['ELMT_3401633', 7.33123060039]
    ['ELMT_3401636', 11.7592497692]
    ['ELMT_3401637', 9.93949907204]
    ['ELMT_3401638', 0.0]
    ['ELMT_3401639', 6.95198458669]
    ['Elmt_3401639', 6.95198458669]
    ['ELMT_3401644', 6.65469610536]
    ['ELMT_3401645', 8.8286277291]


Note how the `Matricks` is represented: as a list of lists, with each sublist containing the 
`probe ID` column(s) followed by the selected sample column(s).   Also note that the first list 
contains the column labels. 

Two create a subset comprised of more than one sample (column) there are two methods available.
One can compose a multi-sample subset using ``union``, ``intersection``, and ``modulus``
methods (or their corresponding operators, ``|``, ``&``, and ``%``.   Bear in mind that this requires the two
`Matrickss` to be sufficiently the same to effect such a composition.  Briefly, this means they need to both
have probe ID (i.e. first) column(s) be the same, both in content and in order.  The expression columns need
not be the same at all.  Probe IDs in one instance are NOT compared with those in another, so if the order isn't the
same, the result will be a dog's breakfast.

So, suppose we wanted to add another sample to the ``r1`` subset we created, above.  We can make another subset

 >>> r2 = a1['probe_id', 'ABC(12)']

and then combine this with the first one to  create a new `Matricks` subset that contains just those two columns
from the original `Matricks`.

 >>> r12 = r1 | r2   
 >>> print r12.getLabels()
   ['probe_id', 'DEFC0N(1)', 'ABC(12)']

 >>> #print r12._data

 >>> for r in r12: print r
    ['ELMT_3401602', 6.6022379846, 7.14727114229]
    ['ELMT_3401603', 6.63635120703, 6.6469632681]
    ['ELMT_3401605', 9.7365656865, 9.33488740366]
    ['ELMT_3401607', 6.75639196465, 6.65137398038]
    ['ELMT_3401612', 7.05322172216, 6.58374160839]
    ['ELMT_3401614', 6.65934616753, 6.59679034883]
    ['ELMT_3401619', 6.67986657646, 6.66351268706]
    ['ELMT_3401623', 6.80554955104, 6.65611759304]
    ['ELMT_3401625', 10.3501936853, 10.6488388784]
    ['ELMT_3401626', 8.10062767869, 7.5310613409]
    ['ELMT_3401628', 6.63538974978, 6.55860431817]
    ['ELMT_3401632', 6.59048802252, 6.97318937509]
    ['ELMT_3401633', 7.33123060039, 7.20203718782]
    ['ELMT_3401636', 11.7592497692, 11.4847211865]
    ['ELMT_3401637', 9.93949907204, 9.15673736606]
    ['ELMT_3401638', 0.0, 0.0]
    ['ELMT_3401639', 6.95198458669, 7.23211276845]
    ['Elmt_3401639', 6.95198458669, 7.23211276845]
    ['ELMT_3401644', 6.65469610536, 6.66459889061]
    ['ELMT_3401645', 8.8286277291, 9.48762418312]


Of course, we don't have to create named instances to do this.  We can write a python statement that will do
it all in one step:

 >>> r3 = a1['probe_id', 'ABC(12)'] | a1['probe_id', 'DEFC0N(1)'] | a1['probe_id', 'F774Lin(3)']
 >>> print r3.getLabels()
    ['probe_id', 'ABC(12)', 'DEFC0N(1)', 'F774Lin(3)']

 >>> for r in r3: print r
    ['ELMT_3401602', 7.14727114229, 6.6022379846, 6.57620493019]
    ['ELMT_3401603', 6.6469632681, 6.63635120703, 6.66361340118]
    ['ELMT_3401605', 9.33488740366, 9.7365656865, 9.39432724993]
    ['ELMT_3401607', 6.65137398038, 6.75639196465, 6.96818993978]
    ['ELMT_3401612', 6.58374160839, 7.05322172216, 6.66963293585]
    ['ELMT_3401614', 6.59679034883, 6.65934616753, 6.53686489577]
    ['ELMT_3401619', 6.66351268706, 6.67986657646, 7.26045576436]
    ['ELMT_3401623', 6.65611759304, 6.80554955104, 6.67254761381]
    ['ELMT_3401625', 10.6488388784, 10.3501936853, 10.0755468901]
    ['ELMT_3401626', 7.5310613409, 8.10062767869, 7.11119485886]
    ['ELMT_3401628', 6.55860431817, 6.63538974978, 6.53825496578]
    ['ELMT_3401632', 6.97318937509, 6.59048802252, 7.47303945599]
    ['ELMT_3401633', 7.20203718782, 7.33123060039, 8.28373011066]
    ['ELMT_3401636', 11.4847211865, 11.7592497692, 12.3247525578]
    ['ELMT_3401637', 9.15673736606, 9.93949907204, 10.7308783293]
    ['ELMT_3401638', 0.0, 0.0, 13.4779333646]
    ['ELMT_3401639', 7.23211276845, 6.95198458669, 6.69342317943]
    ['Elmt_3401639', 7.23211276845, 6.95198458669, 6.69342317943]
    ['ELMT_3401644', 6.66459889061, 6.65469610536, 6.72401222705]
    ['ELMT_3401645', 9.48762418312, 8.8286277291, 6.65231345481]


Note that with unions, columns are not duplicated.  If there are columns in both `Matricks` instances
with the same label, only the left-hand column will be used in the resulting instance.   Even though
you could theoretically select samples from two different parent `Matricks` instances, sample labels should be
(and, in practice, always are) unique.  Consequently, we assume samples with the same label are the same
sample and therefore need not be duplicated when composing.

Python slice attributes can be lists as well as strings or numbers.   This provides
an alternate way of construcing subsets from a larger `Matricks`.
To do this, we simply take a slice, passing the list of samples, rather than just one
sample name, as the first (or only) element of the slice.
To create a new `Matricks` that includes only the ``DEFC0N(1) and ``ABC(12)`` 
samples::

 >>> r5 = a1[['probe_id', 'DEFC0N(1)', 'ABC(12)']]
 >>> print r5.getLabels()
    ['probe_id', 'DEFC0N(1)', 'ABC(12)']

 >>> for r in r5: print r
    ['ELMT_3401602', 6.6022379846, 7.14727114229]
    ['ELMT_3401603', 6.63635120703, 6.6469632681]
    ['ELMT_3401605', 9.7365656865, 9.33488740366]
    ['ELMT_3401607', 6.75639196465, 6.65137398038]
    ['ELMT_3401612', 7.05322172216, 6.58374160839]
    ['ELMT_3401614', 6.65934616753, 6.59679034883]
    ['ELMT_3401619', 6.67986657646, 6.66351268706]
    ['ELMT_3401623', 6.80554955104, 6.65611759304]
    ['ELMT_3401625', 10.3501936853, 10.6488388784]
    ['ELMT_3401626', 8.10062767869, 7.5310613409]
    ['ELMT_3401628', 6.63538974978, 6.55860431817]
    ['ELMT_3401632', 6.59048802252, 6.97318937509]
    ['ELMT_3401633', 7.33123060039, 7.20203718782]
    ['ELMT_3401636', 11.7592497692, 11.4847211865]
    ['ELMT_3401637', 9.93949907204, 9.15673736606]
    ['ELMT_3401638', 0.0, 0.0]
    ['ELMT_3401639', 6.95198458669, 7.23211276845]
    ['Elmt_3401639', 6.95198458669, 7.23211276845]
    ['ELMT_3401644', 6.65469610536, 6.66459889061]
    ['ELMT_3401645', 8.8286277291, 9.48762418312]

As we saw earlier, sample names can be regular expressions, allowing us
to specify a subset using a pattern.   If we had another `LSK` column (say, `ABC(13)`)
we could create another `Matricks` instance with just those two columns
thusly::

 >>> r5lsk = a1.get(['probe_id', 'ABC.*'], re=True)
 >>> print r5lsk.getLabels()
    ['probe_id', 'ABC(12)', 'ABC(13)']

 >>> for r in r5lsk: print r
    ['ELMT_3401602', 7.14727114229, 1.682159]
    ['ELMT_3401603', 6.6469632681, 1.682159]
    ['ELMT_3401605', 9.33488740366, 1.682159]
    ['ELMT_3401607', 6.65137398038, 1.682159]
    ['ELMT_3401612', 6.58374160839, 1.682159]
    ['ELMT_3401614', 6.59679034883, 1.682159]
    ['ELMT_3401619', 6.66351268706, 1.682159]
    ['ELMT_3401623', 6.65611759304, 1.682159]
    ['ELMT_3401625', 10.6488388784, 1.682159]
    ['ELMT_3401626', 7.5310613409, 1.682159]
    ['ELMT_3401628', 6.55860431817, 1.682159]
    ['ELMT_3401632', 6.97318937509, 1.682159]
    ['ELMT_3401633', 7.20203718782, 1.682159]
    ['ELMT_3401636', 11.4847211865, 1.682159]
    ['ELMT_3401637', 9.15673736606, 1.682159]
    ['ELMT_3401638', 0.0, 1.682159]
    ['ELMT_3401639', 7.23211276845, 1.682159]
    ['Elmt_3401639', 7.23211276845, 1.682159]
    ['ELMT_3401644', 6.66459889061, 1.682159]
    ['ELMT_3401645', 9.48762418312, 1.682159]


Just as we can join two samples, you can also take their intersection::

 >>> r3a = r3 & a1['probe_id', 'CDDB4(5)']  # This should result in an essentially null set.
 >>> print a1.labels
    ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']

 >>> print r3a.getLabels()
    ['probe_id']

 >>> for r in r3a: print r
    ['ELMT_3401602']
    ['ELMT_3401603']
    ['ELMT_3401605']
    ['ELMT_3401607']
    ['ELMT_3401612']
    ['ELMT_3401614']
    ['ELMT_3401619']
    ['ELMT_3401623']
    ['ELMT_3401625']
    ['ELMT_3401626']
    ['ELMT_3401628']
    ['ELMT_3401632']
    ['ELMT_3401633']
    ['ELMT_3401636']
    ['ELMT_3401637']
    ['ELMT_3401638']
    ['ELMT_3401639']
    ['Elmt_3401639']
    ['ELMT_3401644']
    ['ELMT_3401645']


There is also a way to take the complement of a `Matricks`.  Given a parent `Matricks` **A** and a subset **B** we can obtain 
the complement of **B** -- that is, the samples in **A** that are *not* found in **B** -- by using the ``modulus`` method or operator (%).
Using ``r12`` instance we created earlier, we can find the complementaruy subset thusly::

 >>> # "modulo" of two sets:  a % b is what's left when you remove the rows of b from a.
 >>> r3b = a1 % r12
 >>> print r3b.getLabels()
    ['probe_id', 'ABC(13)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']

 >>> for r in r3b: print r
    ['ELMT_3401602', 1.682159, 6.6318799406, 6.63021747852, 6.57620493019]
    ['ELMT_3401603', 1.682159, 6.70026291599, 6.67341553263, 6.66361340118]
    ['ELMT_3401605', 1.682159, 8.88887581915, 8.70271863949, 9.39432724993]
    ['ELMT_3401607', 1.682159, 6.70203184527, 7.05207191931, 6.96818993978]
    ['ELMT_3401612', 1.682159, 6.62893626542, 6.51635952774, 6.66963293585]
    ['ELMT_3401614', 1.682159, 6.54032931162, 6.5067348291, 6.53686489577]
    ['ELMT_3401619', 1.682159, 6.57837221187, 6.78383553317, 7.26045576436]
    ['ELMT_3401623', 1.682159, 6.64764879202, 6.6403692878, 6.67254761381]
    ['ELMT_3401625', 1.682159, 9.26241934526, 9.84545402073, 10.0755468901]
    ['ELMT_3401626', 1.682159, 9.24637465474, 11.2541801046, 7.11119485886]
    ['ELMT_3401628', 1.682159, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401632', 1.682159, 6.68431036403, 6.67796164216, 7.47303945599]
    ['ELMT_3401633', 1.682159, 6.93376501527, 7.40407740412, 8.28373011066]
    ['ELMT_3401636', 1.682159, 10.8845553078, 10.7344737293, 12.3247525578]
    ['ELMT_3401637', 1.682159, 8.84061428541, 9.69594817225, 10.7308783293]
    ['ELMT_3401638', 1.682159, 13.4536343874, 13.5199773001, 13.4779333646]
    ['ELMT_3401639', 1.682159, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 1.682159, 6.96898611023, 6.68270691586, 6.69342317943]
    ['ELMT_3401644', 1.682159, 6.59303032509, 6.63139625302, 6.72401222705]
    ['ELMT_3401645', 1.682159, 7.66907923624, 8.4171269045, 6.65231345481]

The `pop` method works like a cross between the python ``dict``'s `pop` method
and the `matricks.modulus` method, here.  If no arguments are specified, `pop` 
returns a copy of the instance with all but the last (right-most) column.  If
a list of columns is provided, the result will have all but those columns in it.

 >>> print a1
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401602' 7.14727114229 1.682159 ... 6.6318799406 6.63021747852 6.57620493019],
      ['ELMT_3401603' 6.6469632681 1.682159 ... 6.70026291599 6.67341553263 6.66361340118],
      ['ELMT_3401605' 9.33488740366 1.682159 ... 8.88887581915 8.70271863949 9.39432724993],
    ...  
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['ELMT_3401644' 6.66459889061 1.682159 ... 6.59303032509 6.63139625302 6.72401222705],
      ['ELMT_3401645' 9.48762418312 1.682159 ... 7.66907923624 8.4171269045 6.65231345481]]

 >>> a1pop = a1.pop()
 >>> print a1pop
    [['ABC(12)' 'ABC(13)' 'DEFC0N(1)' 'CDDB4(5)' 'Jovi(1)'],
      [7.14727114229 1.682159 6.6022379846 6.6318799406 6.63021747852],
      [6.6469632681 1.682159 6.63635120703 6.70026291599 6.67341553263],
      [9.33488740366 1.682159 9.7365656865 8.88887581915 8.70271863949],
    ...  
      [7.23211276845 1.682159 6.95198458669 6.96898611023 6.68270691586],
      [6.66459889061 1.682159 6.65469610536 6.59303032509 6.63139625302],
      [9.48762418312 1.682159 8.8286277291 7.66907923624 8.4171269045]]

 >>> a1pop = a1.pop(['ABC(13)', 'Jovi(1)'])
 >>> print a1pop
    [['ABC(12)' 'DEFC0N(1)' 'CDDB4(5)' 'F774Lin(3)'],
      [7.14727114229 6.6022379846 6.6318799406 6.57620493019],
      [6.6469632681 6.63635120703 6.70026291599 6.66361340118],
      [9.33488740366 9.7365656865 8.88887581915 9.39432724993],
    ...  
      [7.23211276845 6.95198458669 6.96898611023 6.69342317943],
      [6.66459889061 6.65469610536 6.59303032509 6.72401222705],
      [9.48762418312 8.8286277291 7.66907923624 6.65231345481]]


Selecting Rows
,,,,,,,,,,,,,,

One or more rows may be extracted from a `Matricks` instance by using the `extractRows` method,
passing it a string or sequence listing the key column value(s) for the row(s) of interest.  This returns
another (presumably smaller) `Matricks` instance that contains only the selected rows.

For example, to extract the row with key element ``ELMT_3401628``::

 >>> swatch = a1.extractRows('ELMT_3401628')
 >>> for r in swatch: print r
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]

To get more than one, specify more than one or specify a list::

 >>> swatch = a1.extractRows('ELMT_3401628', 'ELMT_3401605')
 >>> for r in swatch: print r
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]

 >>> swatch = a1.extractRows(['ELMT_3401628', 'ELMT_3401605'])
 >>> for r in swatch: print r
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]

If more than one row's key column (default: column 0) matches, all matching rows will
be returned::

 >>> swatch = a1.extractRows('ELMT_3401639')
 >>> for r in swatch: print r
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]

What should be immediately obvious is that row IDs are case-insensitive.  We could just have
easily looked for ``eLmT_3401639`` and come up with the same result.  To get rows that
match without folding, use ``fold=False``::

 >>> swatch = a1.extractRows('ELMT_3401639', fold=False)
 >>> for r in swatch: print r
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]


An argument may also be a slice, but this must be constructed more or less explicitly.  This 
notation is used to specify an absolute range of rows.  For instance, suppose we wanted to 
get the rows 3 through 18, we would use::

 >>> swatch = a1.extractRows(slice(3,18))
 >>> print swatch
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401607' 6.65137398038 1.682159 ... 6.70203184527 7.05207191931 6.96818993978],
      ['ELMT_3401612' 6.58374160839 1.682159 ... 6.62893626542 6.51635952774 6.66963293585],
      ['ELMT_3401614' 6.59679034883 1.682159 ... 6.54032931162 6.5067348291 6.53686489577],
    ...  
      ['ELMT_3401638' 0.0 1.682159 ... 13.4536343874 13.5199773001 13.4779333646],
      ['ELMT_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943]]


We even must do our own arithmetic.  If we wanted to get every other row, we can use the `step`
component of the slice, as would normally be used in any list.  To get all the odd-numbered rows
in the instance::

 >>> swatch = a1.extractRows(slice(1,None,2))
 >>> print swatch
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401603' 6.6469632681 1.682159 ... 6.70026291599 6.67341553263 6.66361340118],
      ['ELMT_3401607' 6.65137398038 1.682159 ... 6.70203184527 7.05207191931 6.96818993978],
      ['ELMT_3401614' 6.59679034883 1.682159 ... 6.54032931162 6.5067348291 6.53686489577],
    ...  
      ['ELMT_3401638' 0.0 1.682159 ... 13.4536343874 13.5199773001 13.4779333646],
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['ELMT_3401645' 9.48762418312 1.682159 ... 7.66907923624 8.4171269045 6.65231345481]]


Rows can be further reduced by supplying `extractRows` with a *discriminator* function using the ``discrim=`` keyword argument.
This should be a function that takes a row as its sole argument and returns ``True`` or ``False``, depending on
whether the row is to be included in the result or not.  Note that this still requires a range of rows to be provided.

Example:  Suppose you want to select only those rows with that do not contain null (``None``) values::

 >>> no_nulls = a1.extractRows(*range(len(a1)), discrim=lambda r: (None not in r))
 >>> for row in no_nulls: print row
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978]
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585]
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577]
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436]
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381]
    ['ELMT_3401625', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901]
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886]
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066]
    ['ELMT_3401636', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578]
    ['ELMT_3401637', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293]
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646]
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705]
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481]


Value Range Selections
----------------------

Rows can be selected by specifying lower and upper boundaries, returning
only those profiles that satisfy these criteria.    Range selection uses the same (slice) 
semantics as sample selection, above, with the first slice component specifying the
sample label.  However the result will contain all samples, not just
the one specified for the range selection.   The profiles returned will include only those 
for which the expression values for the specified sample fall within the given range. 

The range is specified using the second and third slice components to specify the low and high
bounds of the search range.  As in regular slicing, either of these may be omitted, permitting
upper bound-only or lower-bound only searches.

For the first example, suppose you wanted to create a subset of our original **a1** `Matricks`
that included only those profiles where the *ABC(12)* expression values are greater than or equal to
7.0.    Note that the upper bound has been omitted, so this search will return a `Matricks` instance
wherein all the `ABC(12)` values are >= 7.0::

 >>> r4 = a1[['probe_id','ABC(12)']:7.0]
 >>> for r in r4: print r
    ['ELMT_3401602', 7.14727114229]
    ['ELMT_3401603', None]
    ['ELMT_3401605', 9.33488740366]
    ['ELMT_3401607', None]
    ['ELMT_3401612', None]
    ['ELMT_3401614', None]
    ['ELMT_3401619', None]
    ['ELMT_3401623', None]
    ['ELMT_3401625', 10.6488388784]
    ['ELMT_3401626', 7.5310613409]
    ['ELMT_3401628', None]
    ['ELMT_3401632', None]
    ['ELMT_3401633', 7.20203718782]
    ['ELMT_3401636', 11.4847211865]
    ['ELMT_3401637', 9.15673736606]
    ['ELMT_3401638', None]
    ['ELMT_3401639', 7.23211276845]
    ['Elmt_3401639', 7.23211276845]
    ['ELMT_3401644', None]
    ['ELMT_3401645', 9.48762418312]


 >>> print [ x[1] >= 7.0 for x in r4 ]
    [True, False, True, False, False, False, False, False, True, True, False, False, True, True, True, False, True, True, False, True]

Here are two other examples, included mainly for testing purposes.  First, one to 
demonstrate the use of both upper and lower bounds::

 >>> r4a = a1[['probe_id','ABC(12)']:7.0:9]
 >>> for r in r4a: print r
    ['ELMT_3401602', 7.14727114229]
    ['ELMT_3401603', None]
    ['ELMT_3401605', None]
    ['ELMT_3401607', None]
    ['ELMT_3401612', None]
    ['ELMT_3401614', None]
    ['ELMT_3401619', None]
    ['ELMT_3401623', None]
    ['ELMT_3401625', None]
    ['ELMT_3401626', 7.5310613409]
    ['ELMT_3401628', None]
    ['ELMT_3401632', None]
    ['ELMT_3401633', 7.20203718782]
    ['ELMT_3401636', None]
    ['ELMT_3401637', None]
    ['ELMT_3401638', None]
    ['ELMT_3401639', 7.23211276845]
    ['Elmt_3401639', 7.23211276845]
    ['ELMT_3401644', None]
    ['ELMT_3401645', None]


 >>> print [ (x[1] >= 7.0 and x[1] < 9) for x in r4a ]
   [True, False, False, False, False, False, False, False, False, True, False, False, True, False, False, False, True, True, False, False]

Here's another to demonstrate just upper bounds::

 >>> r4b = a1[['probe_id','ABC(12)']::6.6]
 >>> for r in r4b: print r
    ['ELMT_3401602', None]
    ['ELMT_3401603', None]
    ['ELMT_3401605', None]
    ['ELMT_3401607', None]
    ['ELMT_3401612', 6.58374160839]
    ['ELMT_3401614', 6.59679034883]
    ['ELMT_3401619', None]
    ['ELMT_3401623', None]
    ['ELMT_3401625', None]
    ['ELMT_3401626', None]
    ['ELMT_3401628', 6.55860431817]
    ['ELMT_3401632', None]
    ['ELMT_3401633', None]
    ['ELMT_3401636', None]
    ['ELMT_3401637', None]
    ['ELMT_3401638', 0.0]
    ['ELMT_3401639', None]
    ['Elmt_3401639', None]
    ['ELMT_3401644', None]
    ['ELMT_3401645', None]


 >>> print [ (x[1] is not None) and (x[1] < 6.6) for x in r4b ]
    [False, False, False, False, True, True, False, False, False, False, True, False, False, False, False, True, False, False, False, False]

Column Subset Specification
---------------------------

Whereas *range* lets us constrain the numeric values within a `Matricks`, *Column Subsets* let us
create a new `Matricks` instance by specifying a subset of columns in an existing instance.

As seen above, a range can be specified by providing explicit numeric values using *slice* semantics.
However, we are often interested in differential expression, wherein we want to know if
tha value in a given sample is higher or lower than the value for other samples in the same
profile.   `Matricks` can generate *comparand* functions on the fly from a list that
specifies the samples to be used in the comparison, as well as the aggregator function
that will be used to compute the scalar value for the comparison.   The internal method that
does this is called `graep` (pronounced like the name of the fruit from which wine is typically
made.)

Graep works by taking a list of sample names (labels) and returning an anonymous function
(created using python's ``lambda`` operator) that will take a row from the same (or *similar*)
`Matricks` instance and return the aggregated values of the expression data in that row
for the specified samples (columns).    The default aggregation function simple
takes the arithmetic mean of the values specified.   The ``agg`` keyword can
optionally be used to specify a different function.   The only requirement for
this to work properly is that it take a sequence type and return a scalar numeric
value.  (You could, in theory, have it return just about anything, or nothing, but,
as we'll see later, this is probably a bad idea.)  Incidentally, the arithmetic mean
was selected as the default aggregation function because that's what was originally
being used in the project for which this was developed.

Suppose we want to use the expression levels in
``ABC(12)``, ``CDDB4(5)`` and ``F774Lin(3)`` samples.   We pass a list with these
sample names to our ``graep`` method and get back a function that, when applied to 
a row within the same `Matricks` instance, returns a scalar for each row, derived from
the ``ABC(12)``, ``CDDB4(5)`` and ``F774Lin(3)`` samples for that row::

 >>> fn1 = a1.graep(['ABC(12)', 'CDDB4(5)', 'F774Lin(3)'])
 >>> print fn1
   <function <lambda> at ...>

We'll use the iterator feature of the `Matricks` to apply our on-the-fly function to each of the
rows in the set.

 >>> p1 = [ fn1(x) for x in a1 ]
 >>> for r in p1: print r
    6.78511867103
    6.67027986176
    9.20603015758
    6.77386525514
    6.62743693655
    6.55799485207
    6.83411355443
    6.65877133296
    9.99560170459
    7.9628769515
    6.5867773616
    7.04351306504
    7.47317743792
    11.5646763507
    9.57607666026
    8.97718925067
    6.96484068604
    6.96484068604
    6.66054714758
    7.93633895806


If we apply upper and or lower bounds as well, this will return a complete sample set,
but with the elements that do not meet the range criteria all set to ``None``.   The test
will be applied to *ALL* samples in the list, but return *ALL* samples in the `Matricks`.

 >>> r6 = a1[['probe_id', 'ABC(12)', 'F774Lin(3)']:7.2]
 >>> print r6.getLabels()
    ['probe_id', 'ABC(12)', 'F774Lin(3)']

 >>> for r in r6:
 ...     print r
    ['ELMT_3401602', None, None]
    ['ELMT_3401603', None, None]
    ['ELMT_3401605', 9.33488740366, 9.39432724993]
    ['ELMT_3401607', None, None]
    ['ELMT_3401612', None, None]
    ['ELMT_3401614', None, None]
    ['ELMT_3401619', None, 7.26045576436]
    ['ELMT_3401623', None, None]
    ['ELMT_3401625', 10.6488388784, 10.0755468901]
    ['ELMT_3401626', 7.5310613409, None]
    ['ELMT_3401628', None, None]
    ['ELMT_3401632', None, 7.47303945599]
    ['ELMT_3401633', 7.20203718782, 8.28373011066]
    ['ELMT_3401636', 11.4847211865, 12.3247525578]
    ['ELMT_3401637', 9.15673736606, 10.7308783293]
    ['ELMT_3401638', None, 13.4779333646]
    ['ELMT_3401639', 7.23211276845, None]
    ['Elmt_3401639', 7.23211276845, None]
    ['ELMT_3401644', None, None]
    ['ELMT_3401645', 9.48762418312, None]

 >>> print [ (None not in [x[1], x[2]])  for x in r6 ]
    [False, False, True, False, False, False, False, False, True, False, False, False, True, True, True, False, False, False, False, False]

Joins
-----

The `join` method allows two tables to be appeneded to one another where matches are found
between the keys (first olumn) of both instances.  This differs from the concatenation
operators in that dissimilar `Matricks` instances can be joined.  For those familiar with
SQL terms, this iss strictkly an *inner join*.  If a row in the calling instance does
not have a corresponding row in the "other" instance, neither row is included in the join.
When a matching row is found, the two are concatenated to form a new, longer row in the
resulting instance.  

Likewise, the column labels are concatenated.  If the second instance has a column with 
the same label as the first, it is modified with a suffix to distinguish it from the
first instance's column. 

Suppose we take a small subste of our test data::

 >>> test_raw_data_2 = [\
 ['probe_id','ABC(12)','ABC(14)'],
 ... ['ELMT_3401602','7.14727114229','1.682159'],
 ... ['ELMT_3401603','6.6469632681','1.682159'],
 ... ]

Create a `Matricks` instance::

 >>> x1 = Matricks(test_raw_data_2, cvt=float)
 >>> print x1
    [['probe_id' 'ABC(12)' 'ABC(14)'],
      ['ELMT_3401602' 7.14727114229 1.682159],
      ['ELMT_3401603' 6.6469632681 1.682159]]


and join it to our larger, original test `Matricks`::

 >>> j1 = a1.join(x1)
 >>> print j1.getLabels()
    ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)', 'ABC(12)', 'ABC(14)']

Here is what we get::

 >>> for r in j1: print r
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019, 7.14727114229, 1.682159]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118, 6.6469632681, 1.682159]

We can also do a sort of outer join.  All this really does is fill in "blank" entries for rows where
there is no match.  Activate this by setting the ``outer=`` option to this filler value.  Can be
anything but ``False``::

 >>> test_raw_data_3 = [
 ... ['probe_id','gene','chromo'],
 ... ['ELMT_999999','xyz','12'],
 ... ]

 >>> md = Matricks(test_raw_data_3, skipcols=3)
 >>> jd = a1.join(md, outer=None)
 >>> print jd.labels
    ['probe_id', 'gene', 'chromo', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']

 >>> for r in jd: print r
    ['ELMT_3401602', None, None, 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019]
    ['ELMT_3401603', None, None, 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118]
    ['ELMT_3401605', None, None, 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]
    ['ELMT_3401607', None, None, 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978]
    ['ELMT_3401612', None, None, 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585]
    ['ELMT_3401614', None, None, 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577]
    ['ELMT_3401619', None, None, 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436]
    ['ELMT_3401623', None, None, 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381]
    ['ELMT_3401625', None, None, 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901]
    ['ELMT_3401626', None, None, 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886]
    ['ELMT_3401628', None, None, 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401632', None, None, 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599]
    ['ELMT_3401633', None, None, 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066]
    ['ELMT_3401636', None, None, 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578]
    ['ELMT_3401637', None, None, 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293]
    ['ELMT_3401638', None, None, 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646]
    ['ELMT_3401639', None, None, 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', None, None, 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['ELMT_3401644', None, None, 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705]
    ['ELMT_3401645', None, None, 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481]

Here's what the same join would look like as a strictly inner join::

 >>> md = Matricks(test_raw_data_3, skipcols=3)
 >>> jd = a1.join(md)
 >>> print jd.labels
    ['probe_id', 'gene', 'chromo', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']
 >>> for r in jd: print r


Analyzing Matricks Data
-----------------------

`Matricks` instances have a number of methods to aide in the analysis
and filtering of the data they contain.  These include tools for sorting, scoring
and determining statistical correlation between profiles.

Sorting
,,,,,,,

The output of the examples so far has been unsorted.   In nearly all cases, however,
the user will want to order the results.
The builtin `sorted` function has been incorporated into the `Matricks` class 
(as the `sorted` method) for
just this purpose.  The method assumes the list to be sorted is the instances internal data,
but otherwise takes the same (keyword) arguments as the built-in equivalent and mainly serves
as a wrapper to this function.  The noteworthy difference is that results are returned sorted
from highest to lowest, rather than from lowest to highest.   This is because in the application
for which this was initially written, most of the time we're interested in the highest 
numbers (expression levels).  The ordering can be reversed by setting ``reverse=False``
when calling this method.

Instead of passing a list as the first argument, this method passes the sample name or
its index in the label list.  Note that sorting takes place on one and only one column,
so the sample name (i.e. label) "globbing" that is permitted for column selection in `getLabel`
or `choi_score` is not permitted here; only a single column name or index may be supplied.
If no sample is specified, the instance will be sorted on the first data column (default,
column 1.)   Here's a sorted version of our example data::

 >>> a1_sorted = a1.sorted()
 >>> for r in a1_sorted: print r
    ['ELMT_3401636', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578]
    ['ELMT_3401625', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901]
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993]
    ['ELMT_3401637', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293]
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886]
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066]
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019]
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599]
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705]
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436]
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381]
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118]
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577]
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585]
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578]
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646]

Notice two things:  first, since we didn't specify a sort column, it used the first column
of numeric data for sorting.  Secondly, the sort order is from highest to lowest.  The application
for which this was originally written was typically concerned with higher values in the dataset
or analysis results.  Specifying ``reversed=False`` in the keyword arguments to the `sorted` method
will cause it to return results ordered low-to-high.

Aggregation
,,,,,,,,,,,

Datasets often contain columns that are closely related and which can be aggregated together
somehow into a single column.      
To satisfy this need, `Matricks` provides
the ``aggregate`` method.  This will take a dictionary or function that maps sample names in
the current instance to new sample names in a new instance.  The corresponding columns will be
aggregated using the optional function provided with ``agg_fn=`` keyword argument, or the default
(arithmetic mean of non-nulls) aggregator function.

Suppose our demo data pertains to cell types and the individual replicates are
denoted by the parenthesized numbers suffixes.  We can derive the cell type
names from the sample names using a regular expression::

 >>> cell_type_pat = re.compile(r'([\w_\-\+\.]+)(\(\w+\))?')

We can then embedd this (compiled) pattern into a function that we'll pass 
to `aggregate`::

 >>> cell_type = lambda s : cell_type_pat.match(s).group(1) if cell_type_pat.match(s) is not None else s
 >>> ag1 = a1.aggregate(cell_type)

Since we didn't provide an alternat aggregator function, the arithmetic mean is used by default.  Notice that
the columns are in not necessarily in the same order as they were in the source instance.  The do none the less
correspond, positionally, to the labels::

 >>> print ag1.getLabels()
    ['probe_id', 'Jovi', 'ABC', 'F774Lin', 'DEFC0N', 'CDDB4']

 >>> for r in ag1: print r
    ['ELMT_3401602', 6.63021747852, 4.414715071145, 6.57620493019, 6.6022379846, 6.6318799406]
    ['ELMT_3401603', 6.67341553263, 4.16456113405, 6.66361340118, 6.63635120703, 6.70026291599]
    ['ELMT_3401605', 8.70271863949, 5.50852320183, 9.39432724993, 9.7365656865, 8.88887581915]
    ['ELMT_3401607', 7.05207191931, 4.16676649019, 6.96818993978, 6.75639196465, 6.70203184527]
    ['ELMT_3401612', 6.51635952774, 4.132950304195, 6.66963293585, 7.05322172216, 6.62893626542]
    ['ELMT_3401614', 6.5067348291, 4.139474674415, 6.53686489577, 6.65934616753, 6.54032931162]
    ['ELMT_3401619', 6.78383553317, 4.17283584353, 7.26045576436, 6.67986657646, 6.57837221187]
    ['ELMT_3401623', 6.6403692878, 4.16913829652, 6.67254761381, 6.80554955104, 6.64764879202]
    ['ELMT_3401625', 9.84545402073, 6.1654989392, 10.0755468901, 10.3501936853, 9.26241934526]
    ['ELMT_3401626', 11.2541801046, 4.60661017045, 7.11119485886, 8.10062767869, 9.24637465474]
    ['ELMT_3401628', 6.68541200426, 4.120381659085, 6.53825496578, 6.63538974978, 6.66347280086]
    ['ELMT_3401632', 6.67796164216, 4.327674187545, 7.47303945599, 6.59048802252, 6.68431036403]
    ['ELMT_3401633', 7.40407740412, 4.44209809391, 8.28373011066, 7.33123060039, 6.93376501527]
    ['ELMT_3401636', 10.7344737293, 6.58344009325, 12.3247525578, 11.7592497692, 10.8845553078]
    ['ELMT_3401637', 9.69594817225, 5.41944818303, 10.7308783293, 9.93949907204, 8.84061428541]
    ['ELMT_3401638', 13.5199773001, 0.8410795, 13.4779333646, 0.0, 13.4536343874]
    ['ELMT_3401639', 6.68270691586, 4.457135884225, 6.69342317943, 6.95198458669, 6.96898611023]
    ['Elmt_3401639', 6.68270691586, 4.457135884225, 6.69342317943, 6.95198458669, 6.96898611023]
    ['ELMT_3401644', 6.63139625302, 4.173378945305, 6.72401222705, 6.65469610536, 6.59303032509]
    ['ELMT_3401645', 8.4171269045, 5.58489159156, 6.65231345481, 8.8286277291, 7.66907923624]



Scoring
,,,,,,,,,,,,

The `scored` method supports the creation of a score for each row in the instance
which can  then be used to sort or  ignore the rows to create a set of rows that
will constitute an result `Matricks` instance.  

Scoring is accomplished through the use of `Scorer` classes.  These classes have
a constructor and a *call* method.  The constructor can be passed parameters that
will initiate the `Scorer` instance, including the `Matricks` instance itself.
The `call` method will be invoked by the `Matricks` instance's `scored` method in
a loop in which each row is passed to the `call` method and the (scalar) result
recorded by appending it to a copy of that row to form the additional column.

There are two `Scorer` classes that are included with this package in *scoring* 
module:  `Choi`, and `GodelPositional`.

**Choi scoring** is named after Dr. Jarny Choi, who first employed it as a 
fast way to 
score expression profiles in the genome exploration tool `GuIDE`, which
he developed at the `Walter and Eliza Hall Institute`_
in 
Melbourne.   It uses structured group notation 
to specify low and high groups with each expression profile and then
culls these into vectors from which the highest of the lows
is subtracted from the lowest of the highs to obtain the score
for that profile.

.. _Walter and Eliza Hall Institute: http://www.wehi.edu.au/

If no low or high is specified, the entire sample (label) list is used.

The result is a `Matricks` instance that includes the probe ID
column(s) and the score column. 

Here is a trivial example, which specifies no low or high group:: 

 >>> #cs1 = a1.choi_score()
 >>> cs1 = a1.scored(Choi(a1), label='choi score', cleanup=False, modal=False)
 >>> print cs1.getLabels()
    ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)', 'choi score']

 >>> if len(cs1) > 0: 
 ...     for r in cs1: print r
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577, -4.9771871675299995]
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578, -5.003253004259999]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118, -5.01810391599]
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705, -5.04185322705]
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381, -5.12339055104]
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978, -5.36991291931]
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585, -5.37106272216]
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019, -5.46511214229]
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, -5.549953768450001]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, -5.549953768450001]
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436, -5.578296764359999]
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599, -5.790880455990001]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066, -6.60157111066]
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481, -7.805465183119999]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993, -8.0544066865]
    ['ELMT_3401625', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901, -8.966679878399999]
    ['ELMT_3401637', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293, -9.048719329299999]
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886, -9.5720211046]
    ['ELMT_3401636', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578, -10.6425935578]
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646, -13.5199773001]

A threshhold may be specified that will limit the rows returned to only those
for which the score falls at or above the threshhold.  Otherwise, all rows
are returned.

 >>> #cs1 = a1.choi_score(thresh=-7.0)
 >>> cs1 = a1.scored(Choi(a1), label='choi score', thresh=-7.0, cleanup=False, modal=False)
 >>> print cs1.getLabels()
    ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)', 'choi score']

 >>> for r in cs1: 
 ...     print r
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577, -4.9771871675299995]
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578, -5.003253004259999]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118, -5.01810391599]
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705, -5.04185322705]
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381, -5.12339055104]
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978, -5.36991291931]
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585, -5.37106272216]
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019, -5.46511214229]
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, -5.549953768450001]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, -5.549953768450001]
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436, -5.578296764359999]
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599, -5.790880455990001]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066, -6.60157111066]

Now let's specify a low and high group.   We'll use the LSK samples
for our low group and the rest of the samples for the high, which we can obtain
using the `modulus` operator::

 >>> lows = a1.getLabels('ABC.*', re=True)
 >>> #highs = (a1 % a1[lows]).getLabels()[1:]  # don't want the "probe_id" label
 >>> print lows
    [['ABC(12)', 'ABC(13)']]
 
 >>> #print highs
    ['CDDB4(5)', 'DEFC0N(1)', 'Jovi(1)', 'F774Lin(3)']

Note that when there are subgroupings of samples, an aggregator
function is applied -- recursively, if need be -- to the group
to reduce it to a scalar that will represent the group.  Thus,
the low and high lists to which ``max`` and ``min`` are applied
will always be lists of scalars.  The default aggregator
function simply takes the arithmetic mean of fht **non-null**
elements in the group.   The ``agg=`` keyword argument may
be used to pass a different aggregator function either to
this method, or to the `Matricks` constructor. 

The Choi score for this is::

 >>> #cs2 = a1.scored(Choi(a1, low=lows, high=highs), label='choi score', cleanup=False, modal=False)
 >>> #for r in cs2: print r
    ['ELMT_3401636', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578, 4.151033636049999]
    ['ELMT_3401637', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293, 3.42116610238]
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993, 3.1941954376599995]
    ['ELMT_3401625', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901, 3.0969204060599997]
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978, 2.53526535508]
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886, 2.5045846884100005]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066, 2.4916669213599993]
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118, 2.4717900729799993]
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381, 2.4712309912799997]
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705, 2.419651379785]
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578, 2.4178733066950002]
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436, 2.40553636834]
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585, 2.3834092235449997]
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577, 2.367260154685]
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599, 2.2628138349749998]
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, 2.225571031635]
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, 2.225571031635]
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019, 2.161489859045]
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481, 1.0674218632499999]
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646, -0.8410795]


** |godel| Positional Scoring** uses |godel| numbering to characterize the pattern of high
and low values across a row as an integer.  The *positional* aspect derives from
the ability of these numbers to indicate the positions, within the row, where
the (relative) low and high values are found.   Rows with the same "fingerprint" will have highs
and lows in the same columns, though the exact values of these *extrema* may, in fact,
differ.   Two rows may each both have two "peaks", but their |godel| numbers will only
be the same if these peaks occur in the same columns for both rows.  
For each row, the mean and standard deviation are determined.  Highs and lows are
then found by seeing of the distance of a given value from the mean exceeds some multiple
of the standard deviation for the row.  Rows that have more than a specified number of extrema
are considered uninteresting or `flat-liners` and their score will be ``None``.

This makes |godel| Positional Scoring (GPS) useful for creating heatmaps.  A `Matricks` instance
sorted using GPS can then be used to create a heatmap in which similarly "shaped" profiles will
be clustered together.

Here is a |godel| positional scoring example for our test `Matricks`::

 >>> gs = a1.scored(GodelPositional(a1, .8, 4), label='godel score', cleanup=False, modal=False)
 >>> print gs.getLabels()
   ['probe_id', 'ABC(12)', 'ABC(13)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)', 'godel score']

 >>> for r in gs:  print r
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646, 30060030]
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066, 507]
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886, 363]
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481, 12]

If we were to depict the pattern of highs and lows in a rough ASCII-art pattern, it would look like this::
 
 ++++++++++++##
 ++++++++++++##
 ##++##....++##
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ##++########++
 ++++++######++

It is readily seen how similarly-shaped rows are now clustered together.

 >>> hlp = a1.scored(HiLoPositional(a1, .5, 8), cleanup=False, modal=False)
 >>> for r in hlp:  print r
    ['ELMT_3401607', 6.65137398038, 1.682159, 6.75639196465, 6.70203184527, 7.05207191931, 6.96818993978, 'Jovi(1):F774Lin(3):DEFC0N(1):CDDB4(5):ABC(12):ABC(13):Jovi(1):F774Lin(3):DEFC0N(1):CDDB4(5):ABC(12):ABC(13)']
    ['ELMT_3401638', 0.0, 1.682159, 0.0, 13.4536343874, 13.5199773001, 13.4779333646, 'Jovi(1):F774Lin(3):CDDB4(5):ABC(13):ABC(12):DEFC0N(1)']
    ['ELMT_3401626', 7.5310613409, 1.682159, 8.10062767869, 9.24637465474, 11.2541801046, 7.11119485886, 'Jovi(1):CDDB4(5):DEFC0N(1):ABC(12):F774Lin(3):ABC(13):Jovi(1):CDDB4(5):DEFC0N(1):ABC(12):F774Lin(3):ABC(13)']
    ['ELMT_3401628', 6.55860431817, 1.682159, 6.63538974978, 6.66347280086, 6.68541200426, 6.53825496578, 'Jovi(1):CDDB4(5):DEFC0N(1):ABC(12):F774Lin(3):ABC(13):Jovi(1):CDDB4(5):DEFC0N(1):ABC(12):F774Lin(3):ABC(13)']
    ['ELMT_3401619', 6.66351268706, 1.682159, 6.67986657646, 6.57837221187, 6.78383553317, 7.26045576436, 'F774Lin(3):Jovi(1):DEFC0N(1):ABC(12):CDDB4(5):ABC(13):F774Lin(3):Jovi(1):DEFC0N(1):ABC(12):CDDB4(5):ABC(13)']
    ['ELMT_3401633', 7.20203718782, 1.682159, 7.33123060039, 6.93376501527, 7.40407740412, 8.28373011066, 'F774Lin(3):Jovi(1):DEFC0N(1):ABC(12):CDDB4(5):ABC(13):F774Lin(3):Jovi(1):DEFC0N(1):ABC(12):CDDB4(5):ABC(13)']
    ['ELMT_3401637', 9.15673736606, 1.682159, 9.93949907204, 8.84061428541, 9.69594817225, 10.7308783293, 'F774Lin(3):DEFC0N(1):Jovi(1):ABC(12):CDDB4(5):ABC(13):F774Lin(3):DEFC0N(1):Jovi(1):ABC(12):CDDB4(5):ABC(13)']
    ['ELMT_3401636', 11.4847211865, 1.682159, 11.7592497692, 10.8845553078, 10.7344737293, 12.3247525578, 'F774Lin(3):DEFC0N(1):ABC(12):CDDB4(5):Jovi(1):DEFC0N(1):ABC(12):CDDB4(5):Jovi(1):ABC(13)']
    ['ELMT_3401644', 6.66459889061, 1.682159, 6.65469610536, 6.59303032509, 6.63139625302, 6.72401222705, 'F774Lin(3):ABC(12):DEFC0N(1):Jovi(1):CDDB4(5):ABC(13):F774Lin(3):ABC(12):DEFC0N(1):Jovi(1):CDDB4(5):ABC(13)']
    ['ELMT_3401632', 6.97318937509, 1.682159, 6.59048802252, 6.68431036403, 6.67796164216, 7.47303945599, 'F774Lin(3):ABC(12):CDDB4(5):Jovi(1):DEFC0N(1):ABC(13):F774Lin(3):ABC(12):CDDB4(5):Jovi(1):DEFC0N(1):ABC(13)']
    ['ELMT_3401612', 6.58374160839, 1.682159, 7.05322172216, 6.62893626542, 6.51635952774, 6.66963293585, 'DEFC0N(1):F774Lin(3):CDDB4(5):ABC(12):Jovi(1):ABC(13):DEFC0N(1):F774Lin(3):CDDB4(5):ABC(12):Jovi(1):ABC(13)']
    ['ELMT_3401605', 9.33488740366, 1.682159, 9.7365656865, 8.88887581915, 8.70271863949, 9.39432724993, 'DEFC0N(1):F774Lin(3):ABC(12):CDDB4(5):Jovi(1):ABC(13):DEFC0N(1):F774Lin(3):ABC(12):CDDB4(5):Jovi(1):ABC(13)']
    ['ELMT_3401623', 6.65611759304, 1.682159, 6.80554955104, 6.64764879202, 6.6403692878, 6.67254761381, 'DEFC0N(1):F774Lin(3):ABC(12):CDDB4(5):Jovi(1):ABC(13):DEFC0N(1):F774Lin(3):ABC(12):CDDB4(5):Jovi(1):ABC(13)']
    ['ELMT_3401614', 6.59679034883, 1.682159, 6.65934616753, 6.54032931162, 6.5067348291, 6.53686489577, 'DEFC0N(1):ABC(12):CDDB4(5):F774Lin(3):Jovi(1):ABC(13):DEFC0N(1):ABC(12):CDDB4(5):F774Lin(3):Jovi(1):ABC(13)']
    ['ELMT_3401603', 6.6469632681, 1.682159, 6.63635120703, 6.70026291599, 6.67341553263, 6.66361340118, 'CDDB4(5):Jovi(1):F774Lin(3):ABC(12):DEFC0N(1):ABC(13):CDDB4(5):Jovi(1):F774Lin(3):ABC(12):DEFC0N(1):ABC(13)']
    ['ELMT_3401645', 9.48762418312, 1.682159, 8.8286277291, 7.66907923624, 8.4171269045, 6.65231345481, 'ABC(12):DEFC0N(1):Jovi(1):CDDB4(5):F774Lin(3):ABC(13):ABC(12):DEFC0N(1):Jovi(1):CDDB4(5):F774Lin(3):ABC(13)']
    ['ELMT_3401625', 10.6488388784, 1.682159, 10.3501936853, 9.26241934526, 9.84545402073, 10.0755468901, 'ABC(12):DEFC0N(1):F774Lin(3):Jovi(1):CDDB4(5):ABC(13):ABC(12):DEFC0N(1):F774Lin(3):Jovi(1):CDDB4(5):ABC(13)']
    ['ELMT_3401602', 7.14727114229, 1.682159, 6.6022379846, 6.6318799406, 6.63021747852, 6.57620493019, 'ABC(12):CDDB4(5):Jovi(1):DEFC0N(1):F774Lin(3):ABC(13):ABC(12):CDDB4(5):Jovi(1):DEFC0N(1):F774Lin(3):ABC(13)']
    ['ELMT_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, 'ABC(12):CDDB4(5):DEFC0N(1):F774Lin(3):Jovi(1):ABC(13):ABC(12):CDDB4(5):DEFC0N(1):F774Lin(3):Jovi(1):ABC(13)']
    ['Elmt_3401639', 7.23211276845, 1.682159, 6.95198458669, 6.96898611023, 6.68270691586, 6.69342317943, 'ABC(12):CDDB4(5):DEFC0N(1):F774Lin(3):Jovi(1):ABC(13):ABC(12):CDDB4(5):DEFC0N(1):F774Lin(3):Jovi(1):ABC(13)']

 >>> x11 = Matricks([[ 'a',  'b',    'c',  'd'], 
 ...                 ['r1',  'r1.1',   4,   5], 
 ...                 ['r2',  'r2.2',  10,  11], 
 ...                 ['r3',  'r3.1',  21,  31]],
 ... skipcols=2, cvt=float)

 >>> print x11.getLabels()
    ['a', 'b', 'c', 'd']

 >>> for r in x11: print r
    ['r1', 'r1.1', 4.0, 5.0]
    ['r2', 'r2.2', 10.0, 11.0]
    ['r3', 'r3.1', 21.0, 31.0]

 >>> a1t = x11.transpose()
 >>> for r in a1t: print r
    ['c', 4.0, 10.0, 21.0]
    ['d', 5.0, 11.0, 31.0]

 >>> a1t2 = a1t.transpose()
 >>> print a1t2.getLabels()
    ['a', 'b', 'c', 'd']

 >>> for r in a1t2: print r
    ['r1', 'r1.1', 4.0, 5.0]
    ['r2', 'r2.2', 10.0, 11.0]
    ['r3', 'r3.1', 21.0, 31.0]

Pearson Product Moment Correlation
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

One of the calculations often performed with expression profiles is
the `Pearson Product Moment Coefficient`_. We can supply any number of profile identifiers 
(probe IDs; not to be confused with sample names or labels)
used to measure the degree to which a given profile correlates to other profiles
within the dataset.

.. _Pearson Product Moment Coefficient: http://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient/

and the result will be comprised of the same profile IDs as the parent instance, but the columns will
be the PPMCs for each of the specified profiles.  For example::

 >>> ppmc1 = a1.pearson('ELMT_3401603', 'ELMT_3401607')
 >>> print ppmc1.getLabels()
    ['probe_id', 'ELMT_3401603', 'ELMT_3401607']

 >>> for r in ppmc1: print r
    ['ELMT_3401602', 0.994093822093825, 0.9873711032775128]
    ['ELMT_3401603', 1.0, 0.9973005780642519]
    ['ELMT_3401605', 0.9916915617370952, 0.986782079274304]
    ['ELMT_3401607', 0.9973005780642521, 1.0]
    ['ELMT_3401612', 0.99514309197709, 0.9911254283033979]
    ['ELMT_3401614', 0.9993463832853486, 0.995628190154687]
    ['ELMT_3401619', 0.9931235819907885, 0.9960653003415773]
    ['ELMT_3401623', 0.9992656673629212, 0.9963006286019747]
    ['ELMT_3401625', 0.9891293485234534, 0.9859142020756926]
    ['ELMT_3401626', 0.888584061331424, 0.8993865912698161]
    ['ELMT_3401628', 0.9996660578403657, 0.9971818078548389]
    ['ELMT_3401632', 0.9883887894688987, 0.9888071562877305]
    ['ELMT_3401633', 0.9811302954812443, 0.9878631745738885]
    ['ELMT_3401636', 0.9885386079431606, 0.9868884611713656]
    ['ELMT_3401637', 0.9794743559750448, 0.9871172256429301]
    ['ELMT_3401639', 0.9951083808697037, 0.9861344481367755]
    ['Elmt_3401639', 0.9951083808697037, 0.9861344481367755]
    ['ELMT_3401644', 0.9995879246226951, 0.9975119140885805]
    ['ELMT_3401645', 0.9368679872321245, 0.92376912222379]

Let's say we want to select only those profiles that have correlation coefficients 
that are greater than 0.99::

 >>> for r in ppmc1[0.99:]: print r
    ['ELMT_3401602', 0.994093822093825, None]
    ['ELMT_3401603', 1.0, 0.9973005780642519]
    ['ELMT_3401605', 0.9916915617370952, None]
    ['ELMT_3401607', 0.9973005780642521, 1.0]
    ['ELMT_3401612', 0.99514309197709, 0.9911254283033979]
    ['ELMT_3401614', 0.9993463832853486, 0.995628190154687]
    ['ELMT_3401619', 0.9931235819907885, 0.9960653003415773]
    ['ELMT_3401623', 0.9992656673629212, 0.9963006286019747]
    ['ELMT_3401625', None, None]
    ['ELMT_3401626', None, None]
    ['ELMT_3401628', 0.9996660578403657, 0.9971818078548389]
    ['ELMT_3401632', None, None]
    ['ELMT_3401633', None, None]
    ['ELMT_3401636', None, None]
    ['ELMT_3401637', None, None]
    ['ELMT_3401639', 0.9951083808697037, None]
    ['Elmt_3401639', 0.9951083808697037, None]
    ['ELMT_3401644', 0.9995879246226951, 0.9975119140885805]
    ['ELMT_3401645', None, None]

This isn't really what we want.
Recall that when range is specified -- with or without sample names -- the range is
applied to *ALL* the samples specified (or to all the samples in the instance of none
are explicitly provided), and *ALL* of the samples in the instance are returned, not
just the one(s) specified, if any.  We could use the ``purge`` method, but this would
only eliminate the rows that have nulls all the way across.  The second row, for instance,
would still be included, even though one of the values is ``None``.

Without first narrowing the set of samples
to just the one(s) we're interested in, *any* profile that has a value that falls in
the specified range will be included.   We need to make use of slice semantics from above, 
to carve out the set of correlation 
coeeficients for an individual profile -- as well as a specific range of them -- 
from this result.  Suppose we wanted just
the coefficients for `ELMT_3401607` that were higher than 0.99::

 >>> e607 = Matricks(ppmc1)['probe_id', 'ELMT_3401607']
 >>> print e607.getLabels()
    ['probe_id', 'ELMT_3401607']

 >>> for r in e607[:0.99]: print r
    ['ELMT_3401602', None]
    ['ELMT_3401603', 0.9973005780642519]
    ['ELMT_3401605', None]
    ['ELMT_3401607', 1.0]
    ['ELMT_3401612', 0.9911254283033979]
    ['ELMT_3401614', 0.995628190154687]
    ['ELMT_3401619', 0.9960653003415773]
    ['ELMT_3401623', 0.9963006286019747]
    ['ELMT_3401625', None]
    ['ELMT_3401626', None]
    ['ELMT_3401628', 0.9971818078548389]
    ['ELMT_3401632', None]
    ['ELMT_3401633', None]
    ['ELMT_3401636', None]
    ['ELMT_3401637', None]
    ['ELMT_3401639', None]
    ['Elmt_3401639', None]
    ['ELMT_3401644', 0.9975119140885805]
    ['ELMT_3401645', None]

Now can eliminate all the null rows with the ``purge=True`` setting
in the constructor, or by invoking the `purge` method::

 >>> for r in e607[0.99:].purge(): print r
    ['ELMT_3401603', 0.9973005780642519]
    ['ELMT_3401607', 1.0]
    ['ELMT_3401612', 0.9911254283033979]
    ['ELMT_3401614', 0.995628190154687]
    ['ELMT_3401619', 0.9960653003415773]
    ['ELMT_3401623', 0.9963006286019747]
    ['ELMT_3401628', 0.9971818078548389]
    ['ELMT_3401644', 0.9975119140885805]

 Distance
 ,,,,,,,,

The `distance` method will return the distance between two rows in a `Matricks` instance
as calculated by the selected function.  The default distance function is the 
`Pearson Product Moment Correlation`, but there are several others.  This method
more or less mirrors the distance functions described in *The C Clustering Library* 
(Hoon, Imoto, Miyano -- Univ. of Tokyo).  (See `distance` method documentation, below.)

Here are several examples::

 >>> print round(a1.distance(1, 2), 4)        # Pearson correlation (default -- 'c')
    0.0083

 >>> print round(a1.distance(1, 2, 'a'), 4)   # Absolute Pearson
    0.0083

 >>> print round(a1.distance(1, 2, 'u'), 4)   # Uncentered Pearson
    0.0014

 >>> print round(a1.distance(1, 2, 'x'), 4)   # Absolute Uncentered Pearson
    0.0014

 >>> print round(a1.distance(1, 2, 's'), 4)   # Spearman's Rank Correlation
    1.1429

 >>> print round(a1.distance(1, 2, 'k'), 4)   # Kendall's Tau (Spearman variation)
    0.1333

 >>> print round(a1.distance(1, 2, 'e'), 4)   # Euclidean
    5.5335

 >>> print round(a1.distance(1, 2, 'b'), 4)   # City Block (aka Manhattan) 
    2.1228

Detection Summary
,,,,,,,,,,,,,,,,,

If we want to know which samples contain values that fall above some threshhold, we can use the
`detection_summary` method.   The algorithm this uses is as follows:

1. Given a list of profiles, construct a list that is the maximum value for each sample
   across this set.

2. Construct a list of sample names that includes the names of samples for which the
   corresponding maximum value (from step 1) exceeds a given threshhold.   If no threshhold is
   specified, use the dataset-wide mean value.


Example::

 >>> print a1.detection_summary('ELMT_3401602','ELMT_3401603','ELMT_3401605','ELMT_3401607')
     ['ABC(12)', 'DEFC0N(1)', 'CDDB4(5)', 'Jovi(1)', 'F774Lin(3)']


Using *Matricks* as a Base Class
--------------------------------

It's easy to use *Matricks* as a base class, but it's important to remember that any superclass 
must provide its own constructor that calls *Matricks* constructor.   A very minimal example::

..code-block:: python

 >>> class MyMat (Matricks):
 ...     def __init__(self, *args, **kwargs):
 ...         super(MyMat, self).__init__(*args, **kwargs)
 
 >>> m_inst = MyMat(test_raw_data, cvt=lambda x: float(x) if len(x) > 0 else None)
 >>> print m_inst
    [['probe_id' 'ABC(12)' 'ABC(13)' ... 'CDDB4(5)' 'Jovi(1)' 'F774Lin(3)'],
      ['ELMT_3401602' 7.14727114229 1.682159 ... 6.6318799406 6.63021747852 6.57620493019],
      ['ELMT_3401603' 6.6469632681 1.682159 ... 6.70026291599 6.67341553263 6.66361340118],
      ['ELMT_3401605' 9.33488740366 1.682159 ... 8.88887581915 8.70271863949 9.39432724993],
    ...  
      ['Elmt_3401639' 7.23211276845 1.682159 ... 6.96898611023 6.68270691586 6.69342317943],
      ['ELMT_3401644' 6.66459889061 1.682159 ... 6.59303032509 6.63139625302 6.72401222705],
      ['ELMT_3401645' 9.48762418312 1.682159 ... 7.66907923624 8.4171269045 6.65231345481]]

You can now pickle this instance and, when unpickled, it will be an instance of ``MyMat``.
If you don't include the ``__init__`` method, or the call to ``super`` therein, the results
will most likely be not what you wanted or expected.


"""

__version__ = "0.3.20"

import logging
log = logging.getLogger(__name__)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import urllib
import time
import math
from types import FunctionType, NoneType
import re
import json
import cPickle

from ppmc import  *

import distance

from scoring import *

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

NaN = float('nan')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Matricks(object):
    """\
A `Matricks` instance can be constructed from several kinds of sources:
 
*string* :
  a source specified by a string is assumed
  to be a URI and `urllib` is used to open and read the source.   This works equally well for
  local files or remotely archived datasets, such as might be found on 
  `ArrayExpress <http://www.ebi.ac.uk/arrayexpress/>`.   

*file or file-like object (e.g. cStringIO object)* :
  the file's contents are read until ``EOF``.  
 
*sequence type (list or tuple)* :
  no splitting is done at all.  It is assumed the input has already
  been split and is now a sequence of sequences.  Conversion is still applied, however, 
  if the data are not already in the desired format. (See ``cvt=``.)
 
*`Matricks`* :
  all the attributes that are substantially
  unique to that instance are deep-copied to this instance.
 
If the input is `string` or `file-like`, it is checked to see if it is in either
JSON or Python *pickle* format.  A JSON string will be processed using ``json.loads``
and then processing continues as though the input were a `sequence type`.  For 
*pickle* input, a new `Matricks` instance is created by calling ``pickle.loads``
with this input, and then the instances attributes are copied to the instance
under construction.  If the string or file input is neither JSON nor pickled, 
the constructor will attempted to treat it like a TSV or CSV file.  The default is
TSV and the record and field separators can be overridden using the ``rsep`` and ``fsep``
options, described below.

Keyword arguments:

*skiprows*: (int -- default 1)
  if the incoming data stream has fewer or more rows than the (default) one
  row expected (for labels), this can be set to a non-negative number of rows
  to ignore before starting actual parsing and processing of the data rows proper.
  This defaults to one.  In cases where there is no label row, for example, this should be set to 
  zero.

*skipcols*: (int -- default 1)
  if there are more than one column being used to moninate the probe or element 
  portion of each expression profile, this keyword argument can be set to
  the number of such columns and they will be ignored when conversion is applied 
  to each of the data elements.  Note that this does NOT change the assumption that
  such (probe ID) columns are the first (i.e. left-most) in the incoming raw data.
  There is, in other words, no way to specify probe ID columns being somewhere in between 
  the other, expression value-bearing columns.    Like ``skiprows``, this, too, defaults
  to 1.
 
*fsep*: (string -- default TAB)
  If the incoming raw data are being read from a file-like stream of some sort,
  fields (i.e. columns) will be split along boundaries delimited by this string.
  Default is the ASCII TAB character.  This will also be used by the ``dump``
  method when writing data to the output stream. 
 
*rsep*: (string -- default NEWLINE)
  If the incoming raw data are being read from a file-like stream of some sort,
  the I/O machinery of the stream itself will almost certainly be employed to
  break the stream up into individual rows.  In the event this does not happen
  (currently, there's really no support for this, however) this keyword 
  argument can be used to delineat row boundaries.   It is also used by ``dump``
  method when writing data to the output stream. 
 
*cvt*: (function -- default: None)
  When reading the incoming data from a stream it is often the cast that
  the expression values themselves are actually ASCII-encoded numerals rather than raw, 
  binary data.   Consequently, a conversion function must be applied to each of
  these elements as the input stream is parsed.   A conversion function can be passed 
  with this argument that accepts a data item and returns the converted form of the item.
  For inatance, if the incoming values are ASCII-encoded text of floating point values,
  the python ``float`` class constructor can be passed as the ``cvt=`` value.  Each
  number will then be passed as though ``float(...)`` had been called, and the floating
  point value will be returned.  Of course, if input is invalid, a bogus value may be
  returned or an exception raised and the programmer should take steps to either 
  check the data first, or make sure the conversion function can handle such exceptions.
 
  Note: this was not the default behaviour prior to version 0.2.7.
 
*keycol* : (int -- default 0)
  The column number used for indexing the rows for later retrieval using the `extractRows`
  method.  This will override any values found in `Matricks` instances being copied by the
  constructor or loaded from a pickle file.
 
*purge*: (boolean -- default ``False``)
  If set to true, rows that contain only nulls (``None``) will be removed from the
  `Expression Matrix`.  Note that the result may be an instance that cannot be combined
  (ANDed or ORed) with other, erstwhile similar instances.
 
*aggr*: (function -- default Matricks.arithmet_mean)
  The function that will be used by the `aggregate` method if a function is
  not explicitly provided.  It will should accept a sequence that includes only
  numeric values to operate on and return either a numerical result or ``None``
  if it encounters an error or exception during processing.

"""
    
    _distFuncs = { 'c': distance.pearson,
                   'a': lambda a, b: distance.pearson(a, b, absolute=True),
                   'u': lambda a, b: distance.pearson(a, b, uncentered=True),
                   'x': lambda a, b: distance.pearson(a, b, uncentered=True, absolute=True),
                   's': distance.spearman,
                   'k': distance.kendallsTau,
                   'e': distance.euclideanDistance,
                   'b': distance.blockDistance,
                   }
    
    def __init__(self, *args, **kwargs):
        # Invoke the superclass's constructor.
        super(Matricks, self).__init__()

        # Only one arg allowed:
        if len(args) > 1:
            raise MatricksError('too many arguments')

        def purge_nulls(m):
            non_null_rows = [ r for r in m._data if len(filter(None, r[m._skipcols:])) > 0 ]
            return non_null_rows
    

        def parse_from_seq(rawlist, cvt):

            def apply_cvt(s, cnvrzn):
                if s == null or (isinstance(s, (str, unicode)) and len(s) < 1): return None
                try:
                    v = cnvrzn(s)
                except:
                    return None
                return v

            # Sometimes we have a training blank line.  Lop these off.
            while len(rawlist[-1]) == 1 and rawlist[-1][0] == '':
                del rawlist[-1]

            # See if this is a GCT file:
            if len(rawlist) > 0 and len(rawlist[0]) == 1 and rawlist[0][0] == '#1.2':
                self._skipcols = 2
                del rawlist[:2]
                cvt = lambda x: float(x) if x is not None else None

            return rawlist[:self._skiprows] + \
                [ list(l[:self._skipcols]) + map(lambda c: apply_cvt(c, cvt), 
                                                 l[self._skipcols:]) for l in rawlist[self._skiprows:] ]

        stats = list([None, None, []])

        null = kwargs.get('null', None)

        # use this function to apply the conversion and gather stats.

        # Iniitialize as thought it will be an empty matricks instance.
        self._data = list(list())
        self._labels = list()
        self._labelmap = dict()
        self._keyindex = dict()
        self._default_agg = kwargs.get('aggr', self.__class__.arithmetic_mean)
        self._version = __version__

        # Several possible cases on construction:
        # 1) No args.   We're creating an empty instance.
        if len(args) == 0:
            self._stats = list([None, None, 0])
            self._skipcols = kwargs.get('skipcols', 0)
            self._skiprows = kwargs.get('skiprows', 0)
            self._keycol = kwargs.get('keycol', 0)
            return
            
        # 2) Solitary arg is another matricks instance. 
        #    a) we're making a (possibly modified) copy
        elif isinstance(args[0], Matricks):
            other = args[0]
            self._data = purge_nulls(other) if kwargs.get('purge', False) else list(other._data)
            self._labels = [ str(x).strip() for x in other._labels ]
            self._labelmap = dict(zip(self._labels, range(len(self._labels))))
            self._skipcols = other._skipcols
            self._skiprows = other._skiprows
            self._default_agg = other._default_agg
            self._stats = list(other._stats)
            self._keycol = other._keycol
            self._keyindex.update(other._keyindex)
            
        # 3) arg is a string.
        elif isinstance (args[0], (str, unicode, file)):

            # a) url or file to load from
            if isinstance(args[0], file):
                rawdata = args[0].read()
            else:
                try:
                    rawdata = urllib.urlopen(args[0]).read()
                except IOError:
                    rawdata = args[0]

            # b) JSONified list of lists
            if rawdata.startswith('[["'):  # maybe ... gtve it a go
                try:
                    self._data = json.loads(args[0])
                except:
                    # Might look like JSON, but it isn't.
                    # At this point, don't know what it could be, so just FAIL here.
                    raise MatricksError("bad initial data: starts with: '" + args[0][:30])
            
            # c) maybe a pickled instance?
            elif (rawdata.startswith('\x80\x02c') or rawdata.startswith('ccopy_reg')) and \
                    rawdata.split()[1] == self.__class__.__name__:
                unpickled = cPickle.loads(rawdata)
                self._data = unpickled._data
                self._stats = unpickled._stats
                self._skipcols = kwargs.get('skipcols', unpickled._skipcols)
                self._skiprows = kwargs.get('skiprows', unpickled._skiprows)
                self._keycol =  unpickled._keycol if hasattr(unpickled, '_keycol') else 0

                # Earlier versions sometimes left cruft at the end of the matricks instance.  Delete this.
                if len(self._data) > 1 and len(self._data[-1]) != len(self._data[self._skiprows]): 
                    del self._data[-1]

                #self._keyindex = unpickled._keyindex if hasattr(unpickled, '_keyindex') else self._index(self._keycol)
                self._keyindex = self._index(self._keycol)

            # d) raw TSV, CSV, or somethingelSV file?
            else:
                rsep = kwargs.get('rsep', '\n')  # Record separator
                fsep = kwargs.get('fsep', '\t')  # Field separator
                cvt = kwargs.get('cvt', Matricks.def_cvt)
  
                self._skipcols = kwargs.get('skipcols', 1)
                self._skiprows = kwargs.get('skiprows', 1)

                 # Try to parse it into a list of lists.
                try:
                    self._data = parse_from_seq(self._trim([ [ x.strip() for x in y] for y in [ rl.split(fsep) for rl in rawdata.split(rsep)]]), cvt)
                    #self._data = parse_from_seq([ [ x.strip() for x in y] for y in [ rl.split(fsep) for rl in rawdata.split(rsep)]], cvt)
                except:
                    import traceback, sys
                    log.error('failure parsing raw (string)')
                    for emsg in traceback.format_exception(*sys.exc_info()): log.warn(emsg)
                    raise MatricksError('failure parsing raw (string) data: "' + rawdata)

                # Purge nulls if purge=True option is set.
                if kwargs.get('purge', False): self._data = purge_nulls(self)

                self._stats = self._calc_stats(self._data[1:])

                # build the row key index
                self._keycol = kwargs.get('keycol', 0)
                self._keyindex = self._index(self._keycol)
                

        # 4) arg is a list of lists?
        elif isinstance(args[0], (list, tuple)) and isinstance(args[0][0], (list, tuple)):
            self._skipcols = kwargs.get('skipcols', 1)
            self._skiprows = kwargs.get('skiprows', 1)
            self._keycol = None
            cvt = kwargs.get('cvt', Matricks.def_cvt)
            #print '!!!!', parse_from_seq(args[0], cvt)
            self._data = parse_from_seq(self._trim(args[0]), cvt)
            #self._data = parse_from_seq(args[0], cvt)
            self._stats = self._calc_stats(self._data[1:])

            # Purge nulls if purge=True option is set.
            if kwargs.get('purge', False): self._data = purge_nulls(self)

                       
            # build the row key index
            self._keycol = kwargs.get('keycol', 0)
            self._keyindex = self._index(self._keycol)
                
        # 5) ... ?
        else:
            raise MatricksError('initial data of unacceptable type: ' + str(type(args[0])))


        # The next line looks a bit complicated but all it does is handle the case
        # where skiprows > 1.  In that case, each lable is the product of 
        # concatenating the column values for the respective column, delimitedd by newlines.
        if len(self._data) > 0 and len(self._data[0]) > 0:
            self._labels = [ "\n".join([str(self._data[i][j]) for i in range(self._skiprows)]) for j in range(len(self._data[0])) ]
        else:
            self._labels = list()
            
        self._labelmap = dict(zip(self._labels, range(len(self._labels))))

        keycol = kwargs.get('keycol')
        if keycol is not None and keycol != self._keycol:
            self._keycol = keycol
            self._keyindex = self._index(keycol)

        # Ta-dah!

            
    @staticmethod
    def _trim(emx):
        """\
Strip leading rows that are empty and leading (left) columns that are empty. 

 >>> t3 = "\\ta\\tb\\tc\\n\\tx\\t1\\t2\\n\\ty\\t3\\t4\\n\\tz\\t9\\t8\\n\\tw\\t10\\t-3\\n"
 >>> t3m = Matricks(t3, cvt=float)
 >>> print t3m.labels
    ['a', 'b', 'c']

 >>> for r in t3m: print r
    ['x', 1.0, 2.0]
    ['y', 3.0, 4.0]
    ['z', 9.0, 8.0]
    ['w', 10.0, -3.0]

(Thanks to Elizabeth Mason, AIBN UQ, for the use case that prompted this.)

"""
        def leftTrim(r):
            while len(r) > 0 and r[0] in (None, ''): 
                #print r
                del r[0]
            return r if len(r) > 0 else None

        return filter(None, [ leftTrim(r) for r in emx ])



    @staticmethod
    def _calc_stats(lofl):
        m = 0
        M = 0
        acc = 0
        al = 0
        for r in lofl:
            r1 = filter(lambda x: x if isinstance(x, (int, float)) else None, r)
            if len(r1) > 0: 
                m, M = min(m, *r1), max(M, *r1)
                acc = acc + sum(r1)
                al = al + len(r1)
        avg = acc / al if al > 0 else 0
        return (m, M, avg) if al > 0 else (None, None, None)


    @staticmethod
    def def_cvt(f): return f

    @property
    def version(self): return self._version

    @property
    def min(self): return self._stats[0]

    @property
    def max(self): return self._stats[1]

    @property
    def mean(self): return self._stats[2]

    @property
    def skipcols(self): return self._skipcols
                
    @property
    def skiprows(self): return self._skiprows
                
    @property
    def keycol(self): return self._keycol

                
    # This construct comes up often enough that I felt it worth (finally)
    # providing a shortcut.  (Makes using Pycluster a bit easier.)
    @property
    def data(self): return [ row[self._skipcols:] for row in self._data[self._skiprows:] ]

    def purge(self, *args, **kwargs):
        """\
Purge null rowws from the set.  This just constructs
another Matricks instance, passing this instance as input
and setting ``purge`` to ``True``.
"""
        return self.__class__(self, purge=True)


    def dump(self, rawsink=None, fsep='\t', rsep='\n'):
        """\
Dump the Matricks instance into the specified persistent store.
This really just calls the dumps method to write to the specified 
*rawsink*, which can be a string (file name) or a writable file-like object.

"""
        close_file = False
        if isinstance(rawsink, (str, unicode)):
            file_out = open(rawsink, 'w')
            close_file = True

        elif isinstance(rawsink, file):
            file_out = rawsink

        else:
            raise MatricksError(str(rawsink) + ' is not a valid recepticle.')

        file_out.write(self.dumps(fsep=fsep, rsep=rsep))
        bytes_out = file_out.tell()
        if close_file: file_out.close()
        
        return bytes_out


    def dumps(self, fsep='\t', rsep='\n'):
        """\
Dump the instance into a TSV-formatted string.  Field and row separators
are TAB and newline, respectively.  These can be changed using the
*fsep* and *rsep* keyword arguments.  See `load`, above, for 
more details.
"""
        acc = list()
        for r in self._data:
            acc.append(fsep.join([(str(c) if c is not None else '') for c in r]))

        return rsep.join (acc)
        

    _re_pat = re.compile(r'[\.\*\[\]\{\}\?]')

    def getLabels(self, *lvec, **kwargs):
        """\
Return the list of sample labels or just the onces specified by index in `lvec`.

kwargs:

*cmpl*: (default -- ``False``)
  If ``True``, will return the complement of the names spacified.

*flat*: (default -- ``False``)
  If ``True``, will return a flattened list.  otherwise, any nexted
  structuring of the labels in `lvec` will be preserved in the 
  returned list.

*re*: (default -- ``False``)
  If ``True``, will look for regular expression characters in the label
  and, if found, will compile the regex and try to find matches for it.
  Otherwise, a simple string comparison is used.

*fold* (default -- ``False``)
  If ``True``, the search is case-insensitive.  (Only applies
  if ``re=False``.)
"""
        complement = kwargs.get('cmpl', False)

        if len(lvec) < 1:
            return list() if complement else list(self._labels) 

        flat = kwargs.get('flat', False)
        folded = (lambda x: x.upper()) if kwargs.get('fold', False) else (lambda x: x)
        folded_labels = [ folded(c) for c in self._labels ]
        regex = kwargs.get('re', False)

        result = list()
        for s in lvec:
            # Specified an index?
            if isinstance(s, int):
                result.append(self._labels[s])  # It better be in range!

            # A string or regular expression, maybe?
            elif isinstance(s, (str, unicode)):
                # The re.sub crap is there so that we don't have to re escape
                # the parentheses.
                if kwargs.get('re', False) and self._re_pat.search(s):  # Looks like a regular expression
                    pat = re.compile(re.sub(r'([^\\])\)', r'\1\)', re.sub(r'([^\\])\(', r'\1\(', s)))
                    sublist = list()
                    for l in self._labels:
                        m = pat.match(l)
                        if m: sublist.append(l)

                    if complement:
                        csub = [ c for c in self._labels if c not in sublist ]
                        sublist = csub

                    if flat:
                        result = result + sublist
                    else:
                        result.append(sublist)

                else:  # normal string
                    if folded(s) in folded_labels:
                        if  complement:
                            result = [ c for c in self._labels if folded(c) != folded(s) ]
                        else:
                            result.append(s)

            # If we have a sublist, recurse ... (what else?)
            elif isinstance(s, (list, tuple)):
                if flat:
                    result = result + self.getLabels(*s)
                else:
                    result.append(self.getLabels(*s))

            else:  # ... and would you like fries with that?
                raise MatricksError('invalid label type: ' + str(s) + str(type(s)))

        return result

    @property
    def labels(self):
        return list(self._labels)
    
    def __getitem__(self, sl, *args, **kwargs):
        """\
Return rows from the schedule based on the key:low:high semantics to find columns with names matching
           key with values that fall in the [low, high] range.

"""
        # Build a list of the columns from which we'll select.
        # sl is a string or a list or tuple:  just one column specified:
        # copy the whole column and be done with it.

        if isinstance(sl, slice):
            if isinstance(sl.start, (float, int)):  # No sample names specified
                rawkeys = list(self._labels)
                sl = slice(rawkeys, sl.start, sl.stop)

            elif sl.start is None:
                rawkeys = list(self._labels)

            else:
                rawkeys = sl.start
                sl = slice (rawkeys, sl.stop, sl.step)

            # Need to see if no label(s) at all was specified.
            # In that case, we assume all columns / samples.
            if isinstance(rawkeys, str): 
                rawkeys = [ rawkeys ]
            elif isinstance(rawkeys, (float, int)):  # No label(s) specified.
                rawkeys = list(self._labels)

        elif isinstance(sl, (str, unicode)):
            rawkeys = [ sl ]

        elif isinstance (sl, (list, tuple)):
            rawkeys = sl

        else:
            raise MatricksError('invalid item key: ' + str(sl) + str(type(sl)))

        # Expand the raw list using getLabels method in case there are
        # regular expressions in any of the keys.
        keys = self.getLabels(*rawkeys, flat=True, cmpl=kwargs.get('cmpl', False), re=kwargs.get('re', False))
        #print '\n>>>>>>>>>>>>',rawkeys,'\n'
        #print '\n>>>>>>>>>>>>',keys,'\n'

        # Convert this to a list of indexes.
        try:
            key_ndx = map (lambda x: self._labelmap[x], [str(y).strip() for y in keys])
        except KeyError:
            raise MatricksError('no such sample: ' + str(keys) + ' : ' + str(type(keys)) + ' : ' + str(self._labelmap))
        
        # Is the keycol in the list, then don't include it.  Otherwise, 
        # We'll need to set the keycol of the new matricks instance
        # to the keycol argument, here.
        if self._keycol in key_ndx:
            new_keycol = key_ndx[self._keycol]
        else:
            new_keycol = 0
        
        # Need to figure out what the new arrangement of skipcols is, too.
        new_skips = [ki for ki in key_ndx if ki < self._skipcols]
        non_skips = [ki for ki in key_ndx if ki not in new_skips]
        new_skipcols = len(new_skips)
        key_ndx = new_skips + non_skips

        # Just the data, ma'am?
        data_only = kwargs.get('dataonly', False)
        
        # Build the raw data collection.
        if not isinstance(sl, slice):
            selected = \
                map(lambda d: [ d[ki] for ki in key_ndx ], self._data)

            if data_only: return selected[self._skiprows:]
            
            return self.__class__(selected, purge=kwargs.get('purge', False),
                                  skipcols=new_skipcols, skiprows=self._skiprows,
                                  keycol=new_keycol)


        # We're looking for a range within the given list of samples.
        # Filter according to the low/high range values specified in the
        # slice.  What this will do is convert all the
        low = sl.stop if sl.stop is not None else (self.min-1)
        high = sl.step if sl.step is not None else (self.max+1)

        filtered = list()
        for row in self._data:
            next_row = list()
            for i in key_ndx:
                next_row.append(None if ((i in key_ndx) and (not isinstance(row[i], (str, unicode))) and (row[i] == None or row[i] < low or row[i] > high)) else row[i])
            filtered.append(next_row)

        if data_only: return filtered
        
        return self.__class__(filtered, purge=kwargs.get('purge', False),
                              skipcols=new_skipcols, skiprows=self._skiprows,
                              keycol=new_keycol)



    def get(self, sl, *args, **kwargs):
        """\
Explicit interface to list/dictionary getitem semantics.  Allows
other flags to be specified.

kwargs:

*dataonly* : boolean (default -- ``False``)
   returns only a list of lists, rather than a `Matricks` instance.

"""
        return self.__getitem__(sl, *args, **kwargs)


    def __len__(self):
        if self._data is not None and len(self._data) > self._skiprows:
            return (len(self._data) - self._skiprows) 
        else:
            return 0

    # Support for iteration
    def __iter__(self):
        return iter(self._data[self._skiprows:])

    # Support for AND, OR, and MODulus of Matrickss

    def union (self, other, purge=False):
        """\
Return an instance that is the union of this instance and the other one,
column-wise.   (This is really just an alias for the `join` method.)

New as of 0.2.26: Only those rows for which the keycol column value is the same
will be included.  

If the keyword argument ``purge`` is set to ``True``, rows
in the new instance that are all ``None`` will be removed.
"""
        # If the key hashcodes are the same, we can be reasonably
        # sure that these are both Matrickss and the rows are aligned.
        if not isinstance(other, Matricks):
            raise MatricksError('other is not a Matricks instance')

        return self.join(other, junc='|')

    __or__ = union

    
    def intersection (self, other, purge=False):
        """\
Return an instance that is the intersection of this instance and the other one,
column-wise.   If the keyword argument ``purge`` is set to ``True``, rows
in the new instance that are all ``None`` will be removed.
"""
        # If the key hashcodes are the same, we can be reasonably
        # sure that these are both Matrickss and the rows are aligned.
        if not isinstance(other, Matricks):
            raise MatricksError('RHS is not a Matricks instance.')

        return self.join(other, junc='&')
    
    __and__ = intersection


    def modulus(self, other, purge=False):
        """\
Return an instance that is the modulus of this instance and the other one,
column-wise.    The new instance will include columns from this instance
that are not found in the other instance.
If the keyword argument ``purge`` is set to ``True``, rows
in the new instance that are all ``None`` will be removed.
"""

        # If the key hashcodes are the same, we can be reasonably
        # sure that these are both Matrickss and the rows are aligned.
        if not isinstance(other, Matricks):
            raise MatricksError('RHS is not a Matricks instance.')

        return self.join(other, junc='%')
    

    __mod__ = modulus


    def pop(self, cols=None):
        """\
Return a copy `Matricks` instance minus the indicated columns.   This works
more or less like the modulus method.  (This was added 2012-07-23 after seeing
it used in PANDAS (and numpy.)   It's there mainly for convenience, but this
functionality has already been there almost from day one.)

If no columns are specified, the last (right-most) column is omitted from the result.

 >>>

"""
        if cols is None: cols = self._labels[-1:]
        get_cols = [ c for c in self._labels[self._skiprows:] if c not in cols ]
        
        return self.__getitem__(get_cols)




    def __str__(self):
        """Return short, stringified depiction, ala NumPy."""

        
        col_list = [ set(range(len(self.labels[:3]))), set(range(len(self.labels) - 3,len(self.labels))) ]
        if col_list[0] & col_list[1]:  # Too few columns, so there's overlap
            col_list = list(col_list[0] | col_list[1])
        elif len(self._labels) == 0:
            return "[[ ... ]]"
        else:
            col_list = list(col_list[0]) + [None] + list(col_list[1]) # More than 6 cols -- no overlap.

        result = """[[""" + " ".join([repr(self.labels[i]) if i is not None else '...' for i in col_list ]) + "],\n"
        for r in self._data[slice(self._skiprows, min(3+self._skiprows, len(self._data)))]:
            result = result + ("  [" + " ".join([repr(r[i]) if i is not None else '...' for i in col_list ]) + "],\n")

        if len(self._data) > 3:  result = result + "...  \n"

        if len(self._data) > 6:
            for r in self._data[-min(3, abs(len(self._data)-self._skiprows-3)):]:
                result = result + ("  [" + " ".join([repr(r[i]) if i is not None else '...' for i in col_list ]) + "],\n")
        result = result[:-2] + "]"
        return result

    def __repr__ (self):
        return self.__class__.__name__ + "(" + str(self) + ")"
    
    
    def graep(self, l, agg=None):
        """\
Generate Recursive Aggregator of Expression Profile (pronounced "grape")

Returns an anonymous function that will return an aggregated result
of the (possibly nested) list specifying which columns (samples) to use
for the expression profile.

The idea is you can specify a list of columns and get back a function that
will aggregate the values in those colunmns when passed a row from the table.

The default aggregator is the arithmetic mean. This may be substituted with
any function that expects a single, numeric vector argument and returns a scalar.
There are several such functions in the `math` standard library, such as
``max`` and ``min``.

You can write your own aggregator, too.  Suppose you wanted the 
mean of the sample instead of the sample mean.  You could define a function::
   
 >>> def  meanOfTheSample(vec):
 ...     sum(vec) / (len(vec) - 1)

and then pass this in as ``agg=meanOfTheSample``.

In addition to passing column labels, one can also specify numeric values (including
numeric constants) which will be included in the aggregator's computation.  As a trivial
example, passing in ``[10, 10, 10, 10]``  will result in a function that will always
return 10.

"""
        if agg is None: agg = self._default_agg
            
        # We have a list:  recurse into it and build a function that will
        # then return the aggregate result for the row passed to that function.
        if isinstance(l, (list, tuple)):
            fn = lambda x: map(lambda r: r(x), [ self.graep(e, agg) for e in l ])
            return lambda m: agg(fn(m))

        # We have a column lable:  return a function that'll
        # return what's at teh corresponding position in the row.
        elif isinstance(l, (str, unicode)):
            return lambda r: r[self._labelmap[l]]

        # We have a constant:  return a function that'll just
        # return the constant.  This is useful for skewing or
        # biasing the result.
        elif isinstance(l, (int, float, long)):
            return lambda d: l


    def profile(self, low, high, lowset=None, highset=None):
        pass

    @staticmethod
    def arithmetic_mean(vec, null=None):
        """\
        Aggregator functions accept a vector and return a scalar.  They
        should be sure to include only non-``None`` elements in the vector.

        This particular function returns the arithmetic sample mean.  It is the
        default aggregator, and also serves as a simple example for other
        such funtions.
        """
        # Make sure to include only non-None elements of vec.
        nvec = [ v for v in vec if isinstance(v, (float, int)) ]
        #print vec, nvec, len(nvec)
        if len(nvec) == 0: return null
        
        # Return scalar result
        return math.fsum(nvec) / len(nvec)

    @staticmethod
    def mode(v, prec=0):
        """\
Computes the mode of vector `v`.  `prec` determines the number of digits
to the right of the decimal point (in ``floats``) to use.  Negative numbers are
allowed in which case, FEWER digits will be used.  For example, if the
vector contains the numbers ``[ 20, 30.9, 28.2, 40.4, 51, 25 ]``, setting `prec` to
1 will compare the numbers ``[ 200, 309, 282, 404, 510, 25 ]``,
whereas a `prec` of -1 will compare the numbers ``[ 2, 3, 2, 4, 5, 2 ]``.
"""
        prec = 10 ** prec

        rd = dict()
        iv = [ (int(x) * prec) for x in v if isinstance(x, (float, int)) ]
        for e in iv:
            if not rd.has_key(e): rd[e] = 0
            rd[e] = rd[e] + 1
            
        return (sorted(rd.iteritems(), cmp=lambda a,b: cmp(a[1], b[1]), reverse=True)[0][0] / prec) \
            if len(rd) > 0 else 0

        

    @staticmethod
    def std_stats(vec):
        """\
Returns the mean and standard deviation for the supplied vector,
excluding ``None`` elements.
"""
        # Filter out non-None values.
        nvec = [ v for v in vec if isinstance(v, (float, int)) ]

        # Trivial case.
        if len(nvec) == 0: return 0.0, 0.0

        mean = math.fsum(nvec) / len(nvec)
        sdev = sqrt(sum(map(lambda x: x**2, [ (mean - v) for v in nvec] )) / len(nvec))

        
        #log.debug('mean: ' + str(mean) + '   std dev: ' + str(sdev))
        return mean, sdev
    


    @staticmethod
    def minimum (vec):
        """\
        Returns the minimum, non-None element in `vec`.  (Note, this is different
        from just using the built-in ``min`` function, which can also be used,
        but doesn't check element's for ``None``.
        """
        # Make sure to include only non-None elements of vec.
        return min(filter(None, vec))
    
    @staticmethod
    def maximum (vec):
        """\
        Returns the maximum, non-None element in `vec`.  (Note, this is different
        from just using the built-in ``max`` function, which can also be used,
        but doesn't check element's for ``None``.
        """
        # Make sure to include only non-None elements of vec.
        return max(filter(None, vec))
    
    
    @staticmethod
    def label_maker(rows):
        """\
Default method for composing labels from (possibly multiple)
rows (skipped rows) at the start of a dataset.
"""
        if len(rows) > 1:
            rows = zip(*rows)
            return [ ':'.join(c) for c in rows ]
        else:
            return rows[0]


    def todict(self, vec):
        """\
Take an expression profile, presumably from this same class instance, 
and return a dictionary with the sample names (labels) associated
(positionally) with the values in vec.  (First vec element is associated 
with first label, etc.

If vec is shorter than the list of labels, the "excess" labels will not be used.
That is, the returned dictionary will have only ``len(vec)`` items.

If vec is longer than the list of labels, the returned dictionary will have
only as many items as there are labels.  Elements of `vec` that have higher
index in the sequence will be omitted from the result.  

(Note this uses the built-in `zip` function, internally, and therefore has
the same functionality.)
"""
        from collections import OrderedDict
        return OrderedDict(zip(self._labels, vec))

        

    def scored(self, sc_cls, thresh=None, agg=None, label='score', null=None, 
               sort=True, reverse=True, modal=False, cleanup=True,
               exclude=None):
        """\
Return a  `Matricks` instance that has an additional, *score* column.
The score is computed using the function specified in the first (i.e. required)
argument.

kwargs:

*sc_cls* : 
 is an instance of a `Scorer` class, the ``__call__`` method of which
 will be passed a row vector from this matrix and should return a scalar result. 
 (See `Scorer` class docs for further info.)  The returned scalar value will
 will be appended to a copy of the row in the resulting `Matricks` instance.
 ``None`` may be returned, too.  If the function throws an exception it will be caught
 and the resulting score will be set to ``None`` with an error message recorded in the
 log that includes the offending row.

*thresh*:
 a floating point value that specifies the score lower bound.  
 Expression profiles with a score below "thresh" will  not be included in the result
 `Matricks`.

*agg*: 
 a function used to aggregate the row values.  This defaults to
 the identity function.   *agg* will be called with a single row as an argument
 and it should return the (aggregated) row as a result.  This will be passed
 directly to the scoring `func` function.

*label*:
 the label to use for the added column; defaults to *score*.

*null*: 
 value that will be used if invocation of the scoring function
 throws an exception.  Default is ``None``.

"""
        # Make sure we have a function
        if not isinstance(sc_cls, Scorer): return None

        # Supply an identity aggregator if none was specified.
        if (agg is None) or not isinstance(agg, FunctionType): agg = lambda x: x   

        # Do we have a thresshold?
        if (thresh is not None) and not isinstance(thresh, (float, int)): thresh = None

        # Now we're ready to iterate through the expression profiles
        # scoring as we go.
        if exclude is None:
            labels = self.getLabels()
        else:
            labels = self.getLabels(exclude, cmpl=True)

        source = self._data[self._skiprows:]
        result = list()

        for row in source:
            try:
                score = sc_cls(row, skip=self.skipcols)
            except:
                import sys
                import traceback
                log.warn('scoring function failed on ' + str(row))
                for emsg in traceback.format_exception(*sys.exc_info()): log.warn(emsg)
                score = null

            if (score is not None) and ((thresh is None) or (score >= thresh)):
                result.append( row + [ score ] )

        if sort:
            
            if isinstance(sort, (str, unicode)): 
                sort = (str(sort).lower()[:3] == 'rev')

            # Modal sort will sort according to the number of rows
            # that have the same key, rather than the key value itself.
            if modal != False:  
                md = dict()
                for e in range(self._skiprows, len(result)):
                    if not md.has_key(result[e][-1]): md[result[e][-1]] = [ ]
                    md[result[e][-1]].append(e)
                m_result = sorted(md.iteritems(), key=lambda v: len(v[1]), reverse=reverse)
                s_result = list()
                for mvec in m_result:
                    s_result.extend([ result[e] for e in mvec[1] ])

            # Non-modal sort simply sorts according to key value.
            else:
                s_result = sorted(result, key=lambda v: v[-1], reverse=reverse)

            result = s_result

        for i in range(self.skiprows):
            result.insert(i, self._data[i] + [ label ])

        if cleanup:
            vlen = len(self.labels)
            c_result = [ r[:vlen] for r in result ]
            result = c_result

        return self.__class__(result, skipcols=self.skipcols, skiprows=self.skiprows)
    

    def detection_summary(self, *profiles, **kwargs):
        """\
Retrieve sample names (i.e. labels) determined by building an aggregate profile
constructed from the maximum sample value across all selected profiles and
returning those samples for which the corresponding maximum falls above
`thresh`.  If no threshhold is specified, the dataset average is used.

kwargs:

*thresh* : (float - default dataset arithmetic mean)
  return sample names for column values over `thresh`
 
*null* : (any - default ``None``)
  return this value for or in place of null value.
"""
        thresh = kwargs.get("thresh", self.mean)
        # log.debug('thresh='+str(thresh))

        null = kwargs.get("null")

        # Get selected profile rows
        plist = self.getProfiles(*profiles)
        if len(plist) < 1: return null   # Or, maybe we retu1863rn a value across all profiles?

        # Combine then into one row by finding
        # The max in each column.
        mash = map(max, zip(*plist)[self._skipcols:])

        return [ self._labels[i+self._skipcols] for i in range(len(mash)) if mash[i] > self.mean ]


    def getProfiles(self, *IDs, **kwargs):
        """\
Returns a `Matricks` instance that includes only
those profiles that have IDs matching those found in the `IDs`
argument(s).
"""
        return [ x for x in self._data if x[:self._skipcols] in [ [ y ] for y in  IDs ] ]
        
        
    def correlated(self, *rowRef, **kwargs):
        """\
Returns a `Matricks` instance in which the rows have been rearranged according to 
the distance of each one to the reference row idicated by `rowRef`.

The `correlated` method will use one of the several distance functions found
in *The C Clustering Library* to compute the distances between a reference
profile and the rest of the profiles, and then sort them, putting the
reference first, followed by the rest in ascending distance order.

 >>> distTestData = '''\
 ... pid\\tC1\\TC2\\TC3\\tC4\\tC5
 ... A\\t1.\\t2.\\t3.\\t4.\\t5.
 ... B\\t5.\\t4.\\t3.\\t2.\\t1.
 ... C\\t6.\\t8.\\t10.\\t12.\\t14.
 ... D\\t.04\\t.05\\t.06\\t.07\\t.08
 ... E\\t109.\\t12.\\t34.2\\t-3.08\\t51.
 ... '''
 >>> corDS = Matricks(distTestData, cvt=lambda x: float(x))
 >>> import ppmc
 >>> for r in range(5):
 ...     for s in range(5):
 ...         print str(corDS._data[r+1][s+1]).rjust(10),
 ...     print
           1.0        2.0        3.0        4.0        5.0
           5.0        4.0        3.0        2.0        1.0
           6.0        8.0       10.0       12.0       14.0
          0.04       0.05       0.06       0.07       0.08
         109.0       12.0       34.2      -3.08       51.0

 >>> for a in range(5):
 ...     for b in range(5):
 ...         print "%10.7f" % ppmc.calcPPMC(corDS._data[a+1][1:], corDS._data[b+1][1:]),
 ...     print
 ...
     1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359
    -1.0000000  1.0000000 -1.0000000 -1.0000000  0.4769359
     1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359
     1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359
    -0.4769359  0.4769359 -0.4769359 -0.4769359  1.0000000
 >>> print '-----'
  -----

R returns::

            [,1]       [,2]       [,3]       [,4]       [,5]
 [1,]  1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359
 [2,] -1.0000000  1.0000000 -1.0000000 -1.0000000  0.4769359
 [3,]  1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359
 [4,]  1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359
 [5,] -0.4769359  0.4769359 -0.4769359 -0.4769359  1.0000000

for this same matrix (transposed, since R operates on columns,
not rows), so the numbers look good.  Here are the R results for
Spearman::

            [,1]       [,2]       [,3]       [,4]       [,5]        
 [1,]  1.0000000 -1.0000000  1.0000000  1.0000000 -0.3000000
 [2,] -1.0000000  1.0000000 -1.0000000 -1.0000000  0.3000000
 [3,]  1.0000000 -1.0000000  1.0000000  1.0000000 -0.3000000
 [4,]  1.0000000 -1.0000000  1.0000000  1.0000000 -0.3000000
 [5,] -0.3000000  0.3000000 -0.3000000 -0.3000000  1.0000000

 >>> for df in 'cauxskeb':
 ...     print df, ':'
 ...     for a in range(5):
 ...         for b in range(5):
 ...             print "%10.7f" % (-corDS.distance(a, b, df)+1),
 ...         print '\\n',
 ...     print
 c :
  1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359 
 -1.0000000  1.0000000 -1.0000000 -1.0000000  0.4769359 
  1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359 
  1.0000000 -1.0000000  1.0000000  1.0000000 -0.4769359 
 -0.4769359  0.4769359 -0.4769359 -0.4769359  1.0000000 
 <BLANKLINE>
 a :
  1.0000000  1.0000000  1.0000000  1.0000000  0.4769359 
  1.0000000  1.0000000  1.0000000  1.0000000  0.4769359 
  1.0000000  1.0000000  1.0000000  1.0000000  0.4769359 
  1.0000000  1.0000000  1.0000000  1.0000000  0.4769359 
  0.4769359  0.4769359  0.4769359  0.4769359  1.0000000 
 <BLANKLINE>
 u :
  1.0000000  0.6363636  0.9864401  0.9782320  0.5129817 
  0.6363636  1.0000000  0.7543365  0.7825856  0.7941628 
  0.9864401  0.7543365  1.0000000  0.9990249  0.6055385 
  0.9782320  0.7825856  0.9990249  1.0000000  0.6276382 
  0.5129817  0.7941628  0.6055385  0.6276382  1.0000000 
 <BLANKLINE>
 x :
  1.0000000  0.6363636  0.9864401  0.9782320  0.5129817 
  0.6363636  1.0000000  0.7543365  0.7825856  0.7941628 
  0.9864401  0.7543365  1.0000000  0.9990249  0.6055385 
  0.9782320  0.7825856  0.9990249  1.0000000  0.6276382 
  0.5129817  0.7941628  0.6055385  0.6276382  1.0000000 
 <BLANKLINE>
 s :
  1.0000000 -1.0000000  1.0000000  1.0000000 -0.3000000 
 -1.0000000  1.0000000 -1.0000000 -1.0000000  0.3000000 
  1.0000000 -1.0000000  1.0000000  1.0000000 -0.3000000 
  1.0000000 -1.0000000  1.0000000  1.0000000 -0.3000000 
 -0.3000000  0.3000000 -0.3000000 -0.3000000  1.0000000 
 <BLANKLINE>
 k :
  1.0000000  0.6000000  1.0000000  1.0000000  0.8000000 
  0.6000000  1.0000000  0.6000000  0.6000000  0.8000000 
  1.0000000  0.6000000  1.0000000  1.0000000  0.8000000 
  1.0000000  0.6000000  1.0000000  1.0000000  0.8000000 
  0.8000000  0.8000000  0.8000000  0.8000000  1.0000000 
 <BLANKLINE>
 e :
  1.0000000 -7.0000000 -50.0000000 -9.6038000 -2979.7132800 
 -7.0000000  1.0000000 -66.0000000 -9.6838000 -2874.8492800 
 -50.0000000 -66.0000000  1.0000000 -105.7238000 -2560.4092800 
 -9.6038000 -9.6838000 -105.7238000  1.0000000 -3155.6785200 
 -2979.7132800 -2874.8492800 -2560.4092800 -3155.6785200  1.0000000 
 <BLANKLINE>
 b :
  1.0000000 -1.4000000 -6.0000000 -1.9400000 -39.4560000 
 -1.4000000  1.0000000 -6.0000000 -1.9400000 -38.6560000 
 -6.0000000 -6.0000000  1.0000000 -8.9400000 -35.6560000 
 -1.9400000 -1.9400000 -8.9400000  1.0000000 -40.8240000 
 -39.4560000 -38.6560000 -35.6560000 -40.8240000  1.0000000 
 <BLANKLINE>

"""
        # Do a Pearson Product Moment correlation, use optimized class.
        distance = kwargs.get('distance', 'c')
        if distance not in self.__class__._distFuncs:
            raise MatricksError('invalid distance function key: ' + str(distance))
        else:
            distFunction = self.__class__._distFuncs[distance]

        # One of the other, possible correlations ...
        # (assume only one rowRef supplied)
        result = list()
        digs = int(math.log10(len(self._data))) + 1
        ref_ndx = self._getValidIndex(rowRef[0])
        ref_prof = self._data[ref_ndx][self._skipcols:]
        for r in self._data[self._skiprows:]:
            dist = distFunction(ref_prof, r[self._skipcols:])
            if dist is not None: result.append(r + [ round(dist, digs) ])

        # Sort
        r2 = sorted(result, key=lambda x: x[-1], reverse=kwargs.get('anti', False))

        # Clean-up unless otherwise directed
        if kwargs.get('clean', True):
            return self.__class__(self._data[:self._skiprows] + [ x[:-1] for x in r2 ], 
                                  skipcols=self._skipcols, skiprows=self._skiprows)
        else:
            return self.__class__([ (x + ['distance']) for x in self._data[:self._skiprows] ] + r2, 
                                  skipcols=self._skipcols, skiprows=self._skiprows)
    

    def pearson(self, *rowRef, **kwargs):
        """\
Return a `Matricks` instance with two (sets of) columns.  The first 
columns contain the usual rowRef ID columns for any `Matricks` instance.
Subsequent columns contain the PPMC for each of the profiles
specified by the rowRef IDs in the `rowRefs` argument.

This method takes into account the fact that some or all  of the elements
in a profile may be nulls.  For each reference profile (rowRef / row)
beoing correlatd, a null map 
is constructd.  This map is then compared to the null map for each profile,
and only those profiles with a matching null map is correlated with the
reference profile.  Otherwise, the correlation value is set to ``None``.

kwargs:

*uncentered* : (boolean) [False]
 if set to ``True`` will use 0.0 for the reference datum rather than the average of
 each row.

"""
        # Determine which profiles will be used for reference.
        #plist = self.getProfiles(*rowRef)
        plist = self.extractRows(*rowRef)
        if len(plist) < 1: 
            raise MatricksError('no such profile: ' + str(rowRef))

        # Function that will build a nullmap for each profile as we go.
        nullmap = lambda v: tuple([ (v[i] is None) for i in range(len(v)) ])

        # If we have more than one reference profile, we don't want to 
        # re-compute the nullmaps for each one.  We'll save the maps from
        # the first pass and re-use them for subsequent passes.
        nullmap_tbl = dict()
        ppmc_list = list()

        for ref_prof in plist:
            # construct the null map
            ref_nullmap = nullmap(ref_prof)

            # Create a new PPMC calculator
            #log.debug('skipcols: ' + str(self._skipcols))
            ppmo = PPMC(filter(None, ref_prof[self._skipcols:]), uncentered=kwargs.get('uncentered', False))
            ppmc_list.append(ref_prof[:self._skipcols] + [ (ppmo(filter(None, x[self._skipcols:])) if nullmap(x) == ref_nullmap else None) for x in self._data[self._skiprows:] ] )

        # Adding the skiprows is a bit tricky since we're synthesizing an additional
        # column.  If there is more than one skiprow, we'll make the elements
        # for the second through last skiprow blank.
        #result = self._data[:self._skiprows]
        #for i in range(self._skiprows):
        #    result[i].append(ppmc_list[i][0])
        #result = [ self._labels[:self._skipcols] + [ l[0] for l in ppmc_list ] ]
        result = list()

        for i in range(len(self._data)):
            result.append( self._data[i][:self._skipcols] + [ pc[i] for pc in ppmc_list ] )

        return self.__class__(result, purge=True, skipcols=self._skipcols)


    def _getValidIndex(self, k):
        """\
Returns the validated index for `k`.  If `k` is a string it will
return the index of the first row with a first element matching
the string.  If `k` is a non-negative integer it will return
the same number plus ``self.skiprows`` provided that 
0 <= `k` < ``len(self)``.  Otherwise, ``None`` is returned.
"""
        if isinstance(k, (str, unicode)):
            ndx = self._keyindex.get(k, [ ])
            return ndx[0] if len(ndx) > 0 else None
        elif isinstance(k, int) and k >= 0 and k < self.__len__():
            return k + self._skiprows
        
        # Invalid value for k if we get here.
        return None



    def distance(self, k1, k2, fn='c'):
        """
Computes the distance (degree of similarity) between two rows, identified
by `k1` and `k2`.  Either may be a string or a non-negative integer.  Strings are
assumed to be keys and will be used to look for row(s) with matching first elements.
Integers are assumed to be the index of the row in the `Matricks` instance.  
(Using integers is slightly faster.)

kwargs:

*fn*: string
 The distance function to be used.  By default,
 Pearson correlation ( 1 - r, actually) is used.  The collection of functions 
 is based on those found in *The C Clustering Library*.  

Other possible distance functions are:

``c`` :
   Pearson Product Moment Correlation (default)

``a`` :
   absolute value of the pearson correlation
 
``u`` :
   uncentered Pearson correlation (equivalent to the cosine of the angle
   between the two vectors.)
 
``x`` :
   absolute uncentered Pearson correlation

``s`` :
   Spearman's rank correlation
 
``k`` :
   Kendall's tau
 
``e`` :
   Euclidean distance
 
``b`` :
   City block (aka Manhattan) distance


The result will be ``None`` if either `k1` or `k2` result in invalid row
indexes, or if the distance funtion selected returns ``None``.
"""
        # Look up the two rows, make sure they both exist
        vk1, vk2 = self._getValidIndex(k1), self._getValidIndex(k2)

        if None in [vk1, vk2]: return NaN

        # Look up the function, make sure IT exists
        dist = self._distFuncs.get(fn)
        if dist is None: return None

        # Do the deed
        result = dist(self._data[vk1][self._skipcols:], self._data[vk2][self._skipcols:])

        return result


    def pearsonAllIze(self, skim=1, thresh=None, **kwargs):
        """\
Return a `Matricks` instance that is the PPMC-sorted (row-wise)
version of the instance.

This uses an optmization technique that assumes that, after sorting,
the top M rows are most like each other and therefore it's not worth 
comparing them again to all the other rows.  Thus, the instance's data
can be whittled down, making this more like a O(log(N^2)) rather than O(N^2).

I think.

"""
        # Make a copy of our data.
        biglist = list(self._data[self.skiprows:])
        result = [ self.labels ]

        if len(biglist) < 1: 
            raise MatricksError('this is an empty matricks instance')

        # Function that will build a nullmap for each profile as we go.
        nullmap = lambda v: tuple([ (v[i] is None) for i in range(len(v)) ])

        # If we have more than one reference profile, we don't want to 
        # re-compute the nullmaps for each one.  We'll save the maps from
        # the first pass and re-use them for subsequent passes.
        nullmap_tbl = dict([(v[0], nullmap(v)) for v in self._data ])
        
        while len(biglist) > 1:
            # The key optimization step:  For iterations after
            # the first one we're taking the profile that is LEAST
            # like the previous reference profile.   Once we've
            # one our correlation, we know we can remove the first "skim"
            # profiles as they will be increasingly less similar to 
            # subsequent profiles as we iterate down the list.  For the 
            # first iteration, it doesn't matter which one we pick, so
            # just pick the last one to keep the logic the same for all 
            # iterations.
            ref_prof = biglist[0]
            ref_prof_rowid = ref_prof[0]
            ref_nullmap = nullmap_tbl[ref_prof_rowid]
            #print ref_prof_rowid

            # Create a new PPMC calculator
            #log.debug('skipcols: ' + str(self._skipcols))
            ppmo = PPMC(filter(None, ref_prof[self._skipcols:]))
            ppmc_list = sorted([ (ppmo(filter(None, x[self._skipcols:])), x) for x in biglist[1:] if nullmap_tbl[x[0]] == ref_nullmap ],
                               key=lambda x: x[0])

            #print ref_prof,'\n',"\n".join([ str(l) for l in ppmc_list[-skim:]])
            #print "-----\n","\n".join([ str(l) for l in ppmc_list[:skim]]),'\n'
            #print '\n'.join([ str(x[0]) for x in ppmc_list[-20:] ]), '\n------------------------'

            if thresh is not None:
                skimmed = filter(lambda x: x >= thresh, ppmc_list)
            else:
                skimmed = ppmc_list[-skim:]
            
            result.extend( [ ref_prof ] + [ p[1] for p in skimmed ] )
            biglist = [ p[1] for p in ppmc_list[:-len(skimmed)] ]

        return self.__class__(result, purge=True, skipcols=self._skipcols)

    
    def aggregate(self, agg_map, agg_fn=None):
        """\
Returne a new `Matricks` in which the columns of this instance
have been aggregated (some used the term *collapsed*) to form a smaller 
number of columns in the new instance.  A typical use would be to
reduce replicate samples to a single column made up of the averages
of the replicates.

*agg_map*:
  must be either a dictionary or a function: 

*dictionary* :
  the keys will be the names of the new columns and the value for each key
  must be a list of existing columns to aggregate.
 
*function* :
  the function should take a sample name (label) for a source sample and
  return the name of the destination sample. 

*agg_fn*:
  is a function that takes a list of values and returns a scalar
  aggregate of those values.   If it is explicitly provided, it defaults to
  the arithmetic mean of all the non-null elements of the list.   

"""
        # First, we'll convert the lists of source labels
        # into anonymous functions, using graep, that we'll
        # associate with the target labels.
        graep_map = dict( [ (self._labels[i], lambda x: x[i]) for i in range(len(self._labels[:self._skipcols])) ] )

        if isinstance(agg_map, FunctionType):
            kmap = dict()
            for l in self._labels[self._skipcols:]:
                nl = agg_map(l)
                if not kmap.has_key(nl):
                    kmap[nl] = list()
                kmap[nl].append(l)
            agg_map = kmap

        if isinstance(agg_map, dict):
            for key,val in agg_map.iteritems():
                graep_map[key] = self.graep(val, agg_fn)

        else:  # Not what we want.
            raise MatricksError(str(agg_map) + ' is neither a dict nor a function')            

        # Now, build the new sequence of sequences that will
        # be used to create the new instance.
        # (Note: I didn't just set agg_result = agg_map.keys(), below
        # because I need to preserve the same ordering of keys and values
        # and calling the keys() and values() methods do not guarantee
        # the same ordering, whereas this approache does.  NLS
        item_map = [ gi for gi in graep_map.iteritems() if gi[0] not in self._labels[:self._skipcols] ]

        agg_result = [ self._data[i][:self._skipcols] + [ lab[0] for lab in item_map ] for i in range(self._skiprows) ]

        for r in self._data[self._skiprows:]:
            # Sometimes we get a row that is empty or otherwise an invalid length.
            # This try block will catch those and omit them from the resulting instance.
            try:
                new_row = r[:self._skipcols] + \
                    [ f[1](r) for f in item_map ]
                agg_result.append(new_row)
            except IndexError:
                pass  

        return self.__class__(agg_result, skipcols=self._skipcols)
        

    collapse = aggregate
            
            
    def sorted(self, skey=None, cmp=None, reverse=True):
        """\
Return a new, sorted `Matricks`.  This is nearly identical
the built-in *sorted* function with the exception that *reverse* defaults
to ``True`` rather than ``False``.

*skey* : (int or string)
 sample name or column index of sample column to sort on.  If none
 is provided, the first data column is used.

*cmp* : (function)
 function to use to compare rows that overrides the default.

*reverse* : (boolean)
 the new instance's rows will be sorted from highest to lowest unless this is
 set to ``False``.
"""
        # Determine / validate which column we'll be sorting on.
        if skey is None: 
            skey = self._skipcols
        elif isinstance(skey, (str, unicode)) and self._labelmap.has_key(skey):
            skey = self._labelmap[skey]
        elif not (isinstance(skey, int) and (skey in range(len(self._labels)))):
            raise MatricksError('invalid sort key: ' + str(skey))

        # Was a comparator function supplied?
        if not isinstance(cmp, (NoneType, FunctionType)):
            raise MatricksError('invalid comparator: ' + str(cmp))

        # Return a new instance, built using the sorted data.
        #log.debug('skey=%r  cmp=%r  reverse=%r' % (skey, cmp, reverse))
        result = self.__class__([self.getLabels()] + \
                                    sorted(self._data[self._skipcols:], 
                                           cmp=cmp, 
                                           key=lambda v: v[skey], 
                                           reverse=reverse),
                                skipcols=self._skipcols)
        return result


    # The next two methods support pickling.
    def __getstate__(self):
        """Returns the current state of the `Matricks` object as a pickleable return."""
        return  {
            '_data': self._data,
            '_labels': self._labels,
            '_labelmap': self._labelmap,
            '_skipcols': self._skipcols,
            '_keycol': self._keycol,
            '_keyindex': self._keyindex,
            '_skiprows': self._skiprows,
            '_stats': self._stats,
            '_version': self._version,
            }


    def __setstate__(self, st):
        """Unpickles an `Matricks` instance that was pickled
using a dict prepared by __getstate__."""
        for attr, val in st.iteritems():
            setattr(self, attr, val)
        self._default_agg = self.arithmetic_mean
        if not hasattr(self, '_keycol'): self._keycol = 0
        self._keyindex = self._index(self._keycol)
        

    def join(self, other, fold=False, junc='dis', outer=False):
        """\
Join two `Matricks` instances to form another, larger instance.  Unless otherwise specified, 
the instances are joined according to matches in the first column of the right-hand instance 
with values in the first column of the left-hand instance.   Matches must be exact, although 
case-sensitivity can be disabled with the ``fold=`` option.

The result will include all the
columns of both instances.  The `skipcol` columns of each will be grouped together, followed 
the rest of the columns of both instances.  Within these subgroups the left-hand instance's 
columns will appear first, then the right-hand's columns.  The columns will appear in the same
order in which they appear in the source instances.   If both instances have identical column
names, the right-hand column names will be prepended with a prefix (default: ``X.``).  There
is one exception to this:  the column used as the key for the join is taken from the left-hand
side and uses the left-hand's column name for that column.

kwargs:

*junc* : string 
  one of ``dis``', ``con``, ``mod``  (default ``mod``)
  Really for internal use only.  The default join is a union
  of the two instances.   If ``junc='con'``, the intersection is
  returned.   If ``join='mod'``, then the modulus (see `modulus` method) 
  is returned.

"""
        # Make sure the other is a matricks instance, too.
        if not isinstance(other, Matricks):
            raise MatricksError(str(other) + ' is not a Matricks instance')

        # Gather the labels from each side into skip and non-skip column groups.
        # Do this by index as we'll need those, rather than the labels themselves
        # when we join the data pro per.
        LH_sc = range(self._skipcols)
        LH_nsc = range(self._skipcols, len(self._labels))
        RH_sc = [ i for i in range(other._skipcols) if i != other._keycol ]
        RH_nsc = [i for i in range(other._skipcols, len(other._labels)) if i != other._keycol ]
        #print '!!!', LH_sc, LH_nsc, RH_sc, RH_nsc

        if junc in ['con', '&']:  
            int_labels = list(set(self._labels).intersection(set(other._labels)))
            LH_sc = [ i for i in range(self._skipcols) if self._labels[i] in int_labels ]
            LH_nsc = [ i for i in range(self._skipcols, len(self._labels)) if self._labels[i] in int_labels ]
            RH_sc = [ i for i in range(other._skipcols) if i != other._keycol and other._labels[i] in int_labels ]
            RH_nsc = [i for i in range(other._skipcols, len(other._labels)) if i != other._keycol and other._labels[i] in int_labels ]
            
        elif junc in ['mod', '%']:  
            mod_labels = set(self._labels).difference(set(other._labels))
            LH_sc = [ i for i in range(self._skipcols) if self._labels[i] in mod_labels ]
            LH_nsc = [ i for i in range(self._skipcols, len(self._labels)) if self._labels[i] in mod_labels ]
            RH_sc = [ i for i in range(other._skipcols) if i != other._keycol and other._labels[i] in mod_labels ]
            RH_nsc = [i for i in range(other._skipcols, len(other._labels)) if i != other._keycol and other._labels[i] in mod_labels ]

            # We have to include the LH keycolumn for this since it may well be excluded otherwise.
            if self._keycol not in LH_sc:
                LH_sc.insert(0, self._keycol)


        if self._keycol not in LH_sc: LH_sc.insert(0, self._keycol)
        # Construct lists of indexes that correspond to the label lists
        result = list()

        result.append([self._labels[i] for i in LH_sc] + \
                          [ other._labels[j] for j in RH_sc] + \
                          [ self._labels[k] for k in LH_nsc ] + \
                          [ other._labels[t] for t in RH_nsc ])        

        row_len = len(result[0])
        nones = [ None ] * row_len
        for r in self._data[self._skiprows:]:
            key = r[self._keycol].upper()
            #print 'KEY:', key, other._keyindex.has_key(key)
            if not other._keyindex.has_key(key): 
                if outer is False: continue
                oth_r_set = [[key] + [outer] * (len(other.labels) - 1)]
            else:
                oth_r_set = [ other._data[i] for i in other._keyindex[key] ]
                #print 'OTHR_SET:', oth_r_set
            last_row = list(nones)
            for oth in oth_r_set:
                new_row = [ r[i] for i in LH_sc] + \
                    [ oth[j] for j in RH_sc] + \
                    [ r[k] for k in LH_nsc ] + \
                    [ oth[t] for t in RH_nsc ]
                if new_row != last_row:
                    result.append(new_row)
                    last_row = new_row

        #print 'RESULT:', result

        return self.__class__(result, skipcols=len(LH_sc) + len(RH_sc), skiprows=1, keycol=self._keycol)


    # JSON support
    def json(self):
        """\
Convenience method that returns JSON-encoded instance (labels + data).
"""
        return json.dumps(self._data)


    def dataTablesObject(self, offset=0, limit=None):

        """\
Prepare the result to be handed back to DataTables server-side processing
functions.  

Kwargs:

*offset* : (0)
   starting row number to return in `aaData``

*limit* : (None)
   if greater than zero, return no more than this many rows in ``aaData``.  Otherwise
   all rows starting at `offset` are returned.

What's returned is a dictionary with the following contents::

 * aoColumns: a list of column heading objects derived from the return of `getLabels`
 * aaData:  a two-D array of data derived from the normal action result dictionary. 
 * iTotalRecords: total number of elements in this instance
 * iTotalDisplayRecords: total number of elements in the `aaData` array
 * sColumns: the list of column names (labels) 

"""
        result = { 'aaData': self._data[offset:offset+limit] if limit is not None else self._data[offset:],
                   'aoColumns': [ {"sTitle": x, "sName": x } for x in self._labels ],
                   'sColumns': self.getLabels(),
                   'iTotalRecords': self.__len__(),
                   'iTotalDisplayRecords': self.__len__(),
                   #'aoColumnDefs': [ {"sName": names[i], "aTargets": [i] } for i in range(len(names)) ],
                   }
        #result['iTotalDisplayRecords'] = len(result['aaData'])

        return result

    def _index(self, keycol=0):
        """\
Index specified column (default: column 0).
"""
        if isinstance(keycol, (str, unicode)):
            keycol = self._getLabels(keycol)[0]

        if keycol is None: 
            keycol = self._keycol

        t0 = time.time()
        keyindex = dict()
        for i in range(self._skiprows, len(self._data)):
            try:
                k = str(self._data[i][keycol]).upper()            
                if not keyindex.has_key(k):
                   keyindex[k] = [ ]
                keyindex[k].append(i)
            except:
                import sys
                import traceback
                log.warn('indexing fail on ' + str(self._data[i]))
                for emsg in traceback.format_exception(*sys.exc_info()): log.warn(emsg)

        t1 = time.time()
        #log.debug('index build in ' + str( t1-t0) + ' s')
        return keyindex
                        

    def extractRows(self, *rows, **kwargs):
        """\
Return a `Matricks` instance that contains the the specified `rows`.  These can be specified
as individual string arguments, or as a sequence containing strings, or sequences.

kwargs:

 *discrim* : (function)
   narrows the extraction range further.  This should be
   a function that takes a row as it's only argument and returns ``True`` or ``False`` depending on
   whether the row is to be included or not. 

 *keycol* : (name or integer)
   indicates which column to use for selection.

 *fold* : ``True`` | ``False``
   case fold before comparison.  (Default: ``True``) 

"""
        rcrs = kwargs.get('rcrs',False)

        discrim = kwargs.get('discrim', lambda x: x)

        fold = kwargs.get('fold', True)

        keycol = kwargs.get('keycol', self._keycol)

        result = list()
        dlen = len(self._data)

        keyindex = self._keyindex if self._keycol == keycol else self._index(keycol)

        for r in rows:
            if isinstance(r, (list, tuple)):
                clump = self.extractRows(*r, rcrs=True, keycol=keycol)

            elif isinstance(r, (str, unicode)):
                ndx = keyindex.get(r.upper(), [ ])
                clump = [ self._data[i] for i in ndx ] 
                    
            elif isinstance(r, slice):
                # Need to adjust slice start/stop to include skiprows
                r = slice((r.start + self._skiprows) if r.start is not None else self._skiprows,
                          (r.stop + self._skiprows) if r.stop is not None else len(self._data),
                          r.step)
                clump = self._data[r] 
                
            elif isinstance(r, int):
                # Need to adjust slice start/stop to include skiprows
                # (We do it with slice semantics b/c this avoids having to check
                # if we're past the end of _data, which we would have to do
                # using normal, subscript (_data[r]) notation.  If r is 
                # beyond len(_data), clump will be [ ].)
                r = r + self._skiprows
                clump = self._data[r:r+1]

            else:
                if kwargs.get('exc', True) is True:
                    raise MatricksError('invalid row specification: ' + str(r))
                else:
                    clump = list()

            for c in clump:
                if discrim(c): result.append(c)

        if rcrs:
            return result
        else:
            return self.__class__(self._data[:self._skiprows] + result, 
                                  skipcols=self._skipcols, skiprows=self._skiprows)


    def transpose(self):
        """\
Returns a transposed version of this instance.  Rows become columns and columns
become rows.
"""
        # By using the '*' notation we pass the _data member of the instance as
        # a list of arguments to zip.  This will take an element of each list 
        # effectively, a column) and create a row with it.  Thus, transposition.
        return self.__class__([list(x) for x in zip(*self._data)], skiprows=self._skipcols, skipcols=self._skiprows)

    
    def res(self, outfile, descr=0, access=0, name="matricks"):
        """\
Emit the matricks to the specified file-like object in RES (GenePattern)
format.  (see http://www.broadinstitute.org/cancer/software/genepattern/tutorial/gp_fileformats.html)

A few liberties are taken:

 * If an element is not ``None`` the PMA value will be "P".  Otherwise, it will be "A".  It will
   never be "M".
 * The *Description* (i.e. second) row will duplicate the information in the first row.

The ``descr=`` specifies the column number to be used for the ``Description`` column in the output.
The ``access=`` specifies the column to be used for the ``Accession`` column in the output.  Both
default to 0.

"""
        # emit the first three rows:
        
        # first row is "Description<TAB>Accession<TAB>" + labels separated by two TABs each.
        # second row is sample descriptors.  Since GP ignores these, so will we, for now.
        outfile.write("Description\tAccession\t" + "\t\t".join(self.labels[self.skipcols:]) + "\n")
        outfile.write("\t" + "\t\t".join(self.labels[self.skipcols:]) + "\n")

        # Third row is number of rows that follow
        outfile.write(str(len(self._data) - self._skiprows) + ('\t' * (len(self._labels[self._skipcols:]) * 2 )) + '\n')
        
        # Now for the rest of the lines:
        for r in self._data[self.skiprows:]:
            out_row = [ ((x, 'P') if x is not None else (x, 'A')) for x in r[self.skipcols:] ]
            outfile.write(("%s\t%s\t" % (r[descr], r[access])) + "\t".join([("%s\t%s" % x) for x in out_row]) + "\n")
                        
        
        
    def gct(self, outfile, name=0, descr=None):
        """\
Emit the matricks to the specified file-like object in GCT (GenePattern)
format.  (see http://www.broadinstitute.org/cancer/software/genepattern/tutorial/gp_fileformats.html)

A few liberties are taken:

 * If an element is not ``None`` the PMA value will be "P".  Otherwise, it will be "A".  It will
   never be "M".
 * The *Description* (i.e. second) row will duplicate the information in the first row.

The ``descr=`` specifies the column number to be used for the ``Description`` column in the output.
The ``access=`` specifies the column to be used for the ``Accession`` column in the output.  Both
default to 0.

"""
        # emit the first three rows:
        
        # first row is the format version number (1.2 as of 2011-06-30)
        # second row is number of profiles (rows) and number of samples (columns)
        outfile.write("#1.2\n")
        outfile.write(str(len(self._data) - self._skiprows) + '\t' + str(len(self._labels) - self._skipcols) + '\n')

        # Third row contains column labels
        outfile.write("NAME\tDescription\t" + "\t".join(self._labels[self._skipcols:]) + '\n')
        
        # Now for the rest of the lines:
        for r in self._data[self.skiprows:]:
            outfile.write(("%s\t%s\t" % (r[name], r[descr] if descr is not None else 'na')) + "\t".join([str(x) for x in r[self._skipcols:]]) + "\n")
                        
        
        


    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class MatricksError(Exception):
    
    def __init__(self, *args, **kwargs):
        super(MatricksError, self).__init__(*args, **kwargs)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    import doctest
    doctest.testmod(optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS ))

        

    
