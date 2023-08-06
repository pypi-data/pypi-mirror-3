from distutils.core import setup

from byteformat import __version__, __author__, __author_email__


setup(
    name = "byteformat",
    py_modules=["byteformat"],
    version = __version__,
    author = __author__,
    author_email = __author_email__,
    url = 'http://pypi.python.org/pypi/byteformat',
    keywords = ["bytes", "human readable", "SI units"],
    description = "Generate human-readable representations of numbers of bytes.",
    long_description = """\
byteformat is a Python library and command line script for displaying numbers
of bytes as strings using standards-compliant human-readable units such as
'23 KB' or '1.25 terabytes'.

    - Supports both official standards and the common de facto standard:

        * SI decimal units, e.g. 1000 bytes = 1 KB;
        * IEC binary units, e.g. 1024 bytes = 1 KiB;
        * Mixed decimal names with binary sizes, e.g. 1024 bytes = 1 KB.

    - Supports the full set of decimal prefixes from kilo- to yotta-
      and the binary prefixes kibi- to yobi-.
    - Generate strings using symbols (e.g. 'KB'), abbreviated names
      ('Kbyte') or full names ('kilobyte').
    - Uses correct plural terms when needed.
    - Automatically selects the best unit for a given number of bytes.
    - Allows the caller to explicitly override that selection and select 
      which unit to use.
    - Easily customise the output without subclassing.
    - Importable as a Python library module.
    - Runs as a command line script.

""",
    license = 'MIT',
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        ],
    )
