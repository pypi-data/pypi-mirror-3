=====================================================
byteformat -- display bytes in human readable formats
=====================================================

Introduction
------------

byteformat is a Python library and command line script for displaying numbers
of bytes as strings using standards-compliant human-readable units such as
'23 KB' or '1.25 terabytes'.


Features
--------

    - Support for the two official and one de facto standards for bytes:

        * SI decimal units, e.g. 1000 bytes = 1 KB;
        * IEC binary units, e.g. 1024 bytes = 1 KiB;
        * Classic units, e.g. 1024 bytes = 1 KB.

    - Supports the full set of decimal prefixes from kilo- to yotta-
      and the binary prefixes kibi- to yobi-.
    - Generate strings using symbols (e.g. 'KB'), abbreviated names
      ('Kbyte') or full names ('kilobyte').
    - Uses correct plural terms when needed.
    - Allows the caller to explicitly choose which unit to use.
    - Automatically selects the best unit for a given number of bytes.
    - Easily customise the output without subclassing.
    - Importable as a Python library module.
    - Runs as a command line script.

Requires Python 2.5 or better.


Installation
------------

byteformat requires Python 2.5 or better. To install, unpack the archive
and run the install command from inside the top directory:

    python setup.py install


Licence
-------

byteformat is licenced under the MIT Licence. See the LICENCE.txt file
and the header of byteformat.py.


Example of use as a Python library
----------------------------------

You can use byteformat as an importable library in Python. For example:

    >>> from byteformat import ByteFormatter
    >>> format = ByteFormatter('mixed')
    >>> format(1572864)
    '1.5 MB'


Example of use as a command line tool
-------------------------------------

You can run byteformat from the shell using with Python's -m switch:

    python -m byteformat [options] n [...]

Example:

    $ python -m byteformat --scheme=mixed 1572864 2048
    1.5 MB
    2 KB


Self-test
---------

The self-test runs the module's doctests. Run the self-test with:

    python -m byteformat --test

which will print the failing tests, if any, otherwise it will print a count
of how many tests were performed. To suppress output if the tests all pass,
use the --quiet switch. To print extra information, use --verbose.


Known Issues
------------

- The API is still subject to change.
- The command line script is incomplete.
- ``byteformat --help`` is currently just a placeholder.


See the CHANGES.txt file for a list of changes.


