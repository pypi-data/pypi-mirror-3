#!/usr/bin/env python


## Module byteformat.py
##
## Copyright (c) 2012 Steven D'Aprano.
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
## CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
## TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
## SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Format numbers of bytes in standards-compliant human-readable units, such
as kilobytes, megabytes, etc. Supports SI decimal units, IEC binary units,
and mixed units with decimal prefixes and binary values.

``byteformat`` can be used as a Python library:

>>> from byteformat import format as fmt
>>> fmt(23500000000)
'23.5 GB'

or as a command-line application:

$ python -m byteformat 23500000000
23.5 GB

For further information about using byteformat as a command-line application,
call ``python -m byteformat --help`` at the command-line.

``byteformat`` provides a single convenience function, ``format``, for simple
but flexible formatting, and a ``ByteFormatter`` class for full customisation.

Bytes are frequently displayed in a number of different formats, such as:

    * 56 kilobytes
    * 32 Mbytes
    * 1024 KiB

and similar. ``byteformat`` supports these combinations and more with the use
of **formatting schemes** and **display styles**.


Formatting schemes
==================

Bytes can be formatted as human-readable strings according to three standard
schemes. These schemes include two official standards, and one unofficial
de facto standard:

    1)  The decimal SI units KB, MB, etc., based on powers of 1000. This
        official standard is frequently used by hard drive manufacturers for
        reporting disk capacity.

    2)  The binary units KiB, MiB, etc., based on powers of 1024. This
        standard was proposed by IEC and has been accepted by a number of
        standards organisations around the world including NIST.

    3)  A "mixed" de facto standard, where the names of decimal units KB, MB,
        etc. are combined with the values of the binary units based on powers
        of 1024. This clashes with the SI standard, but as of 2011 it is
        still in common use by memory manufacturers for reporting memory
        capacity.

    .. NOTE:: Although ``byteformat`` supports mixed units, they are
       discouraged and should be avoided whenever possible.


The ``format`` function and ``ByteFormatter`` class both accept an optional
``scheme`` argument, a case-insensitive string that specifies which standard
to follow. If no scheme is specified, SI units are used.

    ----------  ----------------------------------  -------------------
    Scheme      Description                         Example
    ----------  ----------------------------------  -------------------
    'SI'        Use decimal SI units (default)      1000 bytes = 1 KB
    'IEC'       Use binary units                    1024 bytes = 1 KiB
    'MIXED'     Use SI units with binary values     1024 bytes = 1 KB
    'DECIMAL'   Alias for 'SI'.
    'BINARY'    Alias for 'IEC'.
    ----------  ----------------------------------  -------------------

For example:

>>> format(23500000, scheme='DECIMAL')
'23.5 MB'
>>> format(23500000, scheme='BINARY')
'22.4 MiB'
>>> format(23500000, scheme='MIXED')
'22.4 MB'


Display styles
==============

Both the ``format`` function and ``ByteFormatter`` class accept an optional
``style`` argument, a case-insensitive string which specifies whether to
display bytes using a short unit symbol, a long unit name, or an abbreviated
form.

    ----------  --------------------------------------  ------------------
    Style       Description                             Example
    ----------  --------------------------------------  ------------------
    'short'     Short unit prefix and unit symbol       '45.6 MB'
    'abbrev'    Short unit prefix and full unit name    '45.6 Mbytes'
    'long'      Long unit prefix and full unit name     '45.6 megabytes'
    ----------  --------------------------------------  ------------------

For example:

>>> format(23500000, style='ABBREV')
'23.5 Mbytes'
>>> format(23500000, style='LONG')
'23.5 megabytes'

Styles and schemes can be combined:

>>> format(23500000, style='LONG', scheme='BINARY')
'22.4 mebibytes'


Other formatting options
========================

The ``ByteFormatter`` class allows you to further customise the display of
bytes, e.g. by suppressing plurals or forcing the use of lowercase 'k' in
kilobytes. See the class for further details.


Selecting display units
=======================

By default, both the ``format`` function and ``ByteFormatter`` class will
automatically select the most appropriate unit prefix for the number of
bytes supplied:

>>> format(900, style='LONG')
'900 bytes'
>>> format(900*10**15, style='LONG')
'900 petabytes'


If you prefer to specify the unit yourself, you can force the use of a
specific unit by passing the case-insensitive prefix you want to use:

>>> format(23500000, style='LONG')
'23.5 megabytes'
>>> format(23500000, prefix='K', style='LONG')
'23500 kilobytes'

Prefixes that can be used are:

    ----------  --------------------------  --------------------
    Prefix      Name                        Value
    ----------  --------------------------  --------------------
    '?'         N/A                         Auto-selected
    ''          bytes                       1
    'B'         bytes                       1
    'K'         kilobytes or kibibytes      1000 or 1024
    'M'         megabytes or mebibytes      1000**2 or 1024**2
    'G'         gigabytes or gibibytes      1000**3 or 1024**3
    'T'         terabytes or tebibytes      1000**4 or 1024**4
    'P'         petabytes or pebibytes      1000**5 or 1024**5
    'E'         exabytes or exbibytes       1000**6 or 1024**6
    'Z'         zettabytes or zebibytes     1000**7 or 1024**7
    'Y'         yottabytes or yobibytes     1000**8 or 1024**8
    ----------  --------------------------  --------------------

Regardless of which scheme you use, the prefix is always specified by one
of the single characters above, e.g. 'K' but not 'Ki' or 'KiB'.

"""

from __future__ import division

import sys
import getopt


__version__ = "0.2a"
__date__ = "2012-05-06"
__author__ = "Steven D'Aprano"
__author_email__ = "steve+python@pearwood.info"

__all__ = ['format', 'ByteFormatter']


# === Scheme and style names ===

# Normalised scheme and style names.
SCHEMES = SI, IEC, MIXED = ('SI', 'IEC', 'MIXED')
STYLES = SHORT, ABBREV, LONG = ('SHORT', 'ABBREV', 'LONG')

# Aliases for scheme names.
ALIASES = {'DECIMAL': SI, 'BINARY': IEC}

if __debug__:
    for scheme in SCHEMES:
        assert scheme.isupper()
    for key, value in ALIASES.items():
        assert key.isupper() and value.isupper()
    for style in STYLES:
        assert style.isupper()
    del scheme, key, value, style



# === Unit prefixes ===

# For powers of ten (SI units) and classic powers of two:
PREFIXES = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
LONG_PREFIXES = ['', 'kilo', 'mega', 'giga', 'tera',
                     'peta', 'exa', 'zetta', 'yotta']

# For new-style powers of two (IEC):
PREFIXES2 = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']
LONG_PREFIXES2 = ['', 'kibi', 'mebi', 'gibi', 'tebi',
                      'pebi', 'exbi', 'zebi', 'yobi']

if __debug__:
    for prefix in (PREFIXES, LONG_PREFIXES, PREFIXES2, LONG_PREFIXES2):
        assert len(prefix) == 9
    del prefix



# === Byte formatter class ===

class ByteFormatter(object):
    """ByteFormatter([scheme [, style]]) -> formatter object

    ``ByteFormatter`` instances are callable objects which can flexibly
    format an integer number of bytes into a human-readable string.

    >>> fmt = ByteFormatter()
    >>> fmt(25000)
    '25 KB'
    >>> fmt(43500000000)
    '43.5 GB'

    (See also the ``format`` convenience function.)

    By default, numbers are formatted using decimal SI units. To change this,
    initialise the instance with the ``scheme`` argument:

    >>> fmt = ByteFormatter('BINARY')
    >>> fmt(25000)
    '24.4 KiB'
    >>> fmt(25600)
    '25 KiB'

    See the section **Formatting Schemes** of the module's docstring for
    additional details.


    By default, numbers are formatted using short unit symbols and prefixes
    such as KB, MB, KiB, etc. Using full unit names or an abbreviated style
    are also supported by passing a ``style`` argument, either when calling
    the instance, or by setting a default when initialising it:

    >>> fmt = ByteFormatter(style='LONG')  # Set the default style.
    >>> fmt(1500000)
    '1.5 megabytes'
    >>> fmt(3800000, style='ABBREV')  # Override the default for one call.
    '3.8 Mbytes'

    See the section **Display Styles** of the module's docstring for further
    details.


    If you prefer to do your own formatting, you can call the ``process``
    method to return a tuple (number, unit-string):

    >>> fmt.process(10125)
    (10.125, 'kilobytes')

    See the method docstring for further details.


    Additional customisation
    ========================

    The formatted strings can be futher customised by modifying these
    ByteFormatter attributes:

        ------------  ---------------------------------------------
        Attribute     Description
        ------------  ---------------------------------------------
        places        Control the number of decimal places.
        plurals       Tuple of three flags controlling plurals.
        strict_si     Control the kilo- prefix (SI scheme only).
        use_ints      Control display of exact integers.
        unit          Tuple of (symbol, name) used for unit names.
        ------------  ---------------------------------------------


    places
    ------

    By default, ByteFormatter displays values to one decimal place, unless the
    value is an exact integer (see ``use_ints`` below). To use a different
    number of decimal places, set the ``places`` attribute to a non-negative
    integer.

    >>> fmt = ByteFormatter()
    >>> fmt.places = 5
    >>> fmt(1015)
    '1.01500 KB'


    plurals
    -------

    The ``plurals`` attribute controls whether or not units are displayed as
    plurals. You can set it to a three-tuple of flags, where the first item
    controls plurals for SHORT formatting, the second for ABBREV formatting,
    and the third for LONG formatting.

    By default, ``plurals`` is set to (False, True, True) so SHORT formatting
    does not use plurals, but ABBREV and LONG do. For example:

    >>> fmt = ByteFormatter()
    >>> fmt(7000, style='LONG')
    '7 kilobytes'
    >>> fmt(7000)
    '7 KB'
    >>> fmt.plurals = (True,)*3
    >>> fmt(7000)
    '7 KBs'

        ..NOTE:: Take care with plurals with short SI units, as the
            plural-s clashes with the SI unit for seconds. E.g. 'MBs'
            would strictly mean "megabyte-second".


    strict_si
    ---------

    The SI standard specifies that the symbol for the kilo- prefix is written
    as a lowercase k, not uppercase. By default, ByteFormatter uses uppercase
    K, which is a violation of the standard but the conventional practice in
    the computing industry. To strictly follow the standard, set the
    ``strict_si`` attribute to True.

    >>> fmt = ByteFormatter()
    >>> fmt.strict_si = True
    >>> fmt(2100)
    '2.1 kB'


    use_ints
    --------

    ByteFormatter normally suppresses the fraction portion of the number if it
    is an exact integer values, e.g. returning '42 KB' rather than '42.0 KB'.
    To disable this behaviour and always show the fraction part, set the
    attribute ``use_ints`` to False.

    >>> fmt = ByteFormatter()
    >>> fmt(1000)
    '1 KB'
    >>> fmt.use_ints = False
    >>> fmt(1000)
    '1.0 KB'

    .. NOTE:: Even with ``use_ints`` set to True, numbers may be displayed
       with a zero fraction part. The ".0" is only suppressed if the
       value is an *exact* integer number of the appropriate unit. E.g.:

       >>> ByteFormatter()(1000001)  # Slightly more than one megabyte
       '1.0 MB'


    unit symbol and name
    --------------------

    The ``unit`` property sets the symbol and name used for byte units. By
    default the symbol is 'B' and the name is 'byte'. The symbol is used for
    SHORT style formatting, and the name for ABBREV and LONG style formatting.

    By changing this property, you can use a ByteFormatter instance to format
    numbers which are not strictly bytes. For example, to display numbers
    formatted as bits:

    >>> bit_formatter = ByteFormatter()
    >>> bit_formatter.unit = ('b', 'bit')
    >>> bytes = 1000000
    >>> bit_formatter(bytes*8, style='abbrev')
    '8 Mbits'

        .. NOTE:: ``ByteFormatter`` has no concept that there are eight
           bits in a byte. It will format whatever value you give it.

    The unit symbol must be a single-character string, and the unit name any
    string.

    """
    places = 1
    use_ints = True
    plurals = (False, True, True)
    strict_si = False

    _template = "%s %s"
    _unit = ('B', 'byte')

    def __init__(self, scheme=SI, style=SHORT):
        self.scheme = scheme
        self.style = style

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.scheme, self.style)

    # === Unit symbol and name ===

    @property
    def unit_symbol(self):
        symbol = self._unit[0]
        assert len(symbol) == 1
        return symbol

    @property
    def unit_name(self):
        return self._unit[1]

    def _get_unit(self):
        return self._unit

    def _set_unit(self, unit):
        symbol, name = unit
        self._unit = (symbol, name)

    unit = property(_get_unit, _set_unit)

    # === Schemes and styles ===

    def _normalise_scheme(self, scheme):
        scheme = scheme.strip().upper()
        scheme = ALIASES.get(scheme, scheme)
        if scheme not in SCHEMES:
            raise ValueError('bad scheme %r' % scheme)
        return scheme

    def _normalise_style(self, style):
        style = style.strip().upper()
        if style not in STYLES:
            raise ValueError('bad style %r' % style)
        return style

    def _get_scheme(self):
        s = self._scheme
        assert s in SCHEMES
        return s

    def _set_scheme(self, scheme):
        self._scheme = self._normalise_scheme(scheme)
        try:
            del self._table
        except AttributeError:
            pass

    def _get_style(self):
        s = self._style
        assert s in STYLES
        return s

    def _set_style(self, style):
        self._style = self._normalise_style(style)

    scheme = property(_get_scheme, _set_scheme)
    style = property(_get_style, _set_style)

    # === Lookup table for prefixes ===

    @property
    def table(self):
        try:
            return self._table
        except AttributeError:
            base = self._base_value
            assert base in (1000, 1024)
            table = tuple([(k, base**i) for i,k in enumerate(PREFIXES)])
            self._table = table
            return table

    @property
    def _base_value(self):
        if self.scheme == SI: return 10**3
        else: return 2**10

    def lookup(self, prefix):
        """Return the number of bytes associated with a particular prefix.

        >>> ByteFormatter('SI').lookup('K')
        1000
        >>> ByteFormatter('IEC').lookup('K')
        1024

        """
        prefix = prefix.upper()
        if prefix == 'B': prefix = ''
        table = dict(self.table)
        return table[prefix]

    def select_prefix(self, bytes):
        """Select the best prefix for the given number of bytes.

        >>> ByteFormatter().select_prefix(3000)
        'K'
        >>> ByteFormatter().select_prefix(3000000)
        'M'

        Searches the table for the largest prefix not larger than the absolute
        value of bytes, and returns that prefix. If the number of bytes is
        larger than the greatest prefix, that prefix is used:

        >>> ByteFormatter().select_prefix(10**100)
        'Y'

        """
        bytes = abs(bytes)
        prefix = ''
        for u, size in self.table:
            if size <= bytes:
                prefix = u
            else: break
        return prefix

    # === Formatting methods ===

    def pluralise(self, string):
        """Return string made plural.

        >>> ByteFormatter().pluralise('unit')
        'units'

        """
        return string + 's'

    def _plural(self, style):
        i = {SHORT: 0, ABBREV: 1, LONG: 2}[style]
        return self.plurals[i]

    def _format_value(self, value):
        """Format the numeric part of the display string."""
        if self.use_ints and value == int(value):
            # Drop the decimal point and show no decimal places.
            return "%d" % value
        return "%.*f" % (self.places, value)

    def _get_prefix_symbol(self, prefix):
        if self.scheme == IEC:
            tmp = PREFIXES.index(prefix)
            prefix = PREFIXES2[tmp]
        elif prefix == 'K' and self.scheme == SI and self.strict_si:
            prefix = 'k'
        return prefix

    def _format_short(self, prefix):
        """Return the suffix used for SHORT style formatted bytes.

        >>> ByteFormatter()._format_short('M')
        'MB'

        """
        prefix = self._get_prefix_symbol(prefix)
        return prefix + self.unit_symbol

    def _format_abbrev(self, prefix):
        """Return the suffix used for ABBREV style formatted bytes.

        >>> ByteFormatter()._format_abbrev('M')
        'Mbyte'

        """
        prefix = self._get_prefix_symbol(prefix)
        return prefix + self.unit_name

    def _get_prefix_name(self, prefix):
        p = PREFIXES.index(prefix)
        prefixes = LONG_PREFIXES2 if self.scheme == IEC else LONG_PREFIXES
        return prefixes[p]

    def _format_long(self, prefix):
        """Return the suffix used for LONG style formatted bytes.

        >>> ByteFormatter()._format_long('M')
        'megabyte'

        """
        prefix = self._get_prefix_name(prefix)
        return prefix + self.unit_name


    _DISPATCH = {SHORT: _format_short, LONG: _format_long,
                 ABBREV: _format_abbrev}

    def _format_prefix(self, prefix, style):
        if prefix not in PREFIXES:
            raise ValueError('bad prefix "%s"' % unit)
        func = self._DISPATCH.get(style.upper())
        if func is None:
            raise ValueError('bad style "%s"' % style)
        return func(self, prefix)

    def __call__(self, bytes, prefix=None, style=None):
        """format(bytes [, prefix [, style]]) -> formatted string

        Unit prefixes
        =============

        By default, the ByteFormatter instance will select the best unit to use
        for the given number of bytes. To force a specific unit, pass the unit
        prefix you want:

        .>> fmt(1000000)
        '1 MB'
        .>> fmt(1000000, prefix='K')
        '1000 KB'

        """
        value, unit = self.process(bytes, prefix, style)
        value = self._format_value(value)
        return self._template % (value, unit)

    def process(self, bytes, prefix=None, style=None):
        """instance.process(bytes [, prefix [, style]]) -> (number, unit)


        For example, to display the number of bytes as a data transfer rate:

        >>> fmt = ByteFormatter()
        >>> '%.2f %s/sec' % fmt.process(2050000)
        '2.05 MB/sec'

        """
        if style is None:
            style = self.style
        else:
            style = self._normalise_style(style)
        if prefix is None or prefix == '?':
            prefix = self.select_prefix(bytes)
        size = self.lookup(prefix)
        value = bytes/size
        unit_part = self._format_prefix(prefix, style)
        if self._plural(style) and (abs(value) > 1):
            unit_part = self.pluralise(unit_part)
        return value, unit_part



def format(bytes, prefix='?', style=SHORT, scheme=SI):
    """format(bytes [, prefix [, style [, scheme]]]) -> formatted string

    Format an integer number of bytes to a human-readable string.

    By default, ``format`` automatically selects the most sensible SI unit:

    >>> n = 42*(1024**3)  # 42 binary GB is just over 45 decimal GB.
    >>> format(n)
    '45.1 GB'

    To force the use of a specific unit, pass the prefix you want:

    >>> format(n, prefix='M')
    '45097.2 MB'

    To use binary or mixed units, you can specify the scheme:

    >>> format(n, scheme='BINARY')  # Use the IEC standard.
    '42 GiB'

    You can also control how the unit is spelled by passing an optional
    style argument:

    >>> format(n, scheme='SI', style='LONG', prefix='M')
    '45097.2 megabytes'

    ``format`` is a convenience function for formatting bytes easily. If you
    have a lot of numbers to be processed with the same scheme, it is more
    efficient to create a single ``ByteFormatter`` instance and call that
    repeatedly.
    """
    return ByteFormatter(scheme, style)(bytes, prefix)


# === Command line tool support ===

class CmdTool:
    """Class used for command line tool support."""

    USAGE = 'Usage:\n  python -m byteformat [options] n [...]'
    LONG_VERSION = "byteformat %s %s" % (__version__, __date__)

    HELP = __doc__  # FIXME

    SHORT_OPTIONS = 'hdVtvq'
    LONG_OPTIONS = ['help', 'docs', 'version', 'test', 'verbose', 'quiet',
                    'scheme=', 'style=', 'prefix='
                    ]

    def __init__(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
        opts, self.args = getopt.getopt(
                            argv, self.SHORT_OPTIONS, self.LONG_OPTIONS
                            )
        self.do_help = self.do_docs = self.do_version = self.do_test = False
        self.verbosity = 0
        self.scheme = SI
        self.style = SHORT
        self.prefix = '?'
        self.process_options(opts)

    def process_options(self, opts):
        for o,a in opts:
            if o in ('-h', '--help'):
                self.do_help = True
                break
            elif o in ('-V', '--version'):
                self.do_version = True
                break
            elif o in ('-d', '--docs'):
                self.do_docs = True
                break
            elif o in ('-t', '--test'):
                self.do_test = True
            elif o in ('-v', '--verbose'):
                self.verbosity += 1
            elif o in ('-q', '--quiet'):
                self.verbosity -= 1
            elif o in ('--scheme'):
                self.scheme = a
            elif o in ('--style'):
                self.style = a
            elif o in ('--prefix'):
                self.prefix = a

    def self_test(self, module=None, verbose=None):
        import doctest
        failed, total = doctest.testmod(module, verbose=verbose)
        if total == 0:
            raise ValueError('no doctests defined, cannot run self-test')
        if self.verbosity >= 0 and failed == 0:
            print("Successfully ran %d tests." % total)

    def run(self):
        """Run byteformat as a command-line tool."""
        global __doc__
        if self.do_help:
            print(self.HELP)
        elif self.do_docs:
            print(__doc__)
        elif self.do_version:
            print(self.LONG_VERSION)
        elif self.do_test:
            self.self_test(verbose=self.verbosity >= 1)
        else:
            if not self.args:
                print(self.USAGE)
                return 1
            formatter = ByteFormatter(self.scheme, self.style)
            args = map(int, self.args)
            for arg in args:
                print(formatter(arg, prefix=self.prefix))


if __name__ == '__main__':
    # Run byteformat from the commandline as a tool.
    sys.exit(CmdTool().run())

