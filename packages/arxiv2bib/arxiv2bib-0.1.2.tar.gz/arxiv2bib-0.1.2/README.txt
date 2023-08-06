Provides a command line tool to get metadata for an academic paper
posted at arXiv.org in BibTeX format.

Installation
------------

Use pip::

    $ pip install arxiv2bib

Use easy install::

    $ easy_install arxiv2bib

Download the source and use setup.py::

    $ python setup.py install

If you cannot install, you can use arxiv2bib.py as a standalone executable.


Examples
--------

Basic usage::

    $ arxiv2bib 1001.1001

Request a specific version::

    $ arxiv2bib 1102.0001v2

Request multiple papers at once::

    $ arxiv2bib 1101.0001 1102.0002 1103.0003

Use a list of papers from a text file (one per line)::

    $ arxiv2bib < papers.txt
