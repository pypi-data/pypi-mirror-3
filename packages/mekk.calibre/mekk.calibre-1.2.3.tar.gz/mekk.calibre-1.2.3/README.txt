=============
mekk.calibre
=============

Helper scripts for some Calibre_ tasks. 

Script list
===========

The following scripts are available:

calibre_guess_and_add_isbn

    Checks books without ISBN (set in metadata) for ISBN-like string
    present in leading pages. If found, add it to the metadata (what
    makes it possible to download full metadata, covers, etc).

calibre_convert_docs_to_rtf

    Convert any .doc to .rtf (unless already present) - using
    openoffice.

calibre_add_if_missing

    Checks given directory tree for books not yet present in calibre,
    add them if found. Uses binary file comparison to check whether
    the file is identical (file name and metadata are not used, on
    purpose).

calibre_find_books_missing_in_database

    Checks whether Calibre database directory contains some unregistered
    files and report them if found.

calibre_report_duplicates

    Report duplicates, adding information of which of them are surely
    safe to merge (because duplicated books are identical or because
    formats do not overlap) and which require examination.

calibre_guess_and_add_isbn
--------------------------

Queries Calibre for all books without ISBN, then tries to locate
ISBN inside (via scanning a few leading pages) and updates Calibre
book metadata if ISBN is found.

Run it without parameters::

    calibre_guess_and_add_isbn

Any ISBN numbers found will be added to the book metadata (and the
script will report them). Books are scanned from the newest, so you
can abort (Ctrl-C) script once it handled new books.

Later on ISBN can be used to grab the book metatada and/or book cover
inside Calibre GUI. Just spawn Calibre and look for books with ISBN
set and missing metadata, for example using query like::

     isbn:~[0-9] not publisher:~[a-z]

(above means: isbn contains some digit, publisher does not contain any
letter). Depending on your workflow, you can then either 

- grab metadata automaticaly (mark all those books, right click,
  pick Edit Metadata Information/Download Metadata)

- review each book individually (mark those books, right click,
  pick Edit Metadata Information/Edit Metadata Individually, then
  click Fetch Metadata on every book successively and review whether
  it fits).

calibre_convert_docs_to_rtf
---------------------------

Queries Calibre for all books which have only .doc format, then uses
OpenOffice to convert them to .rtf and add this format as an
alternative.

OpenOffice (and pyuno libraries provided by it) are used in the
process.

Run it without parameters::

    calibre_convert_docs_to_rtf

Note: the script happens to crash on the end of the job (while
finishing).  I haven't diagnosed the reasons (most likely the problem
is in the libraries I use), but the crash is harmless and does not
influence the actual conversion process.


calibre_find_books_missing_in_database
--------------------------------------

Reports the files present inside Calibre library directory but not
present in the database (= not visible in the interface).

The files are reported to standard output. To add them
all to calibre, pipe output. For example::

    calibre_find_books_missing_in_database.py | xargs -d "\n" calibredb add

(but, better, review everything beforehand)

*The problematic scenario may happen for example if Calibre is used
from two or more machines over synchronized or networked directory
and, by mistake, two copies are run simultaneously.*


calibre_add_if_missing
----------------------

Scans given directory and/or specified files, adds to calibre all
books which are not yet present there.

Duplicate checking is done solely according to the file content.  The
file is skipped if identical file is already present in Calibre.
   
I wrote this script to handle *I want to ensure everything is already
imported and can be deleted* scenario.

Example::

    calibre_add_if_missing /home/jan/OldBooks

(and later remove OldBooks if everything is OK).


calibre_report_duplicates
-------------------------

Analyzes calibre database looking for likely duplicates, and reports
them, adding info of which of those are surely identical, and which
require examination.

Do *not* perform any changes, just prints report (as text or html).

Example::

    calibre_report_duplicates

(text output to the console)

    calibre_report_duplicates --html > /tmp/report.html

(HTML output redirected to file).


Installation and configuration
===============================

Prerequisities
--------------

Calibre must be installed, properly configured and has
some database (otherwise it does not make sense to run those scripts).
The:: 

    calibredb

command must be in PATH (or calibredb variable inside .ini file must
be properly set, see below).

Tools providing commands::

    pdftotext
    catdoc 
    djvutxt
    archmage

should be installed and present in PATH (or properly configured in
.ini, or disabled in .ini, see below). On Ubuntu Linux or Debian Linux
those can be installed from standard repositories, just install the
following packages::

    poppler-utils 
    catdoc
    djvulibre-bin
    archmage

Python 2.6 or 2.7 is required (scripts are using some features
introduced in 2.6 - in particular tempfile extensions, subprocess and
namedtuple). Also, lxml library must be installed.  On Debian or
Ubuntu just install the following packages::

   python2.6
   python-lxml

For calibre_convert_docs_to_rtf to work, ootools_ library must be
installed. Simplest method to install it::

    easy_install ootools

(on Ubuntu `sudo easy_install ootools`).

I develop and use those scripts on Ubuntu Linux. They should work on
Windows or Mac if necessary tools are installed, but I've never tried
it.

Actual installation
--------------------

Simple::

    easy_install mekk.calibre

should do. In case you don't want to mess with your system
directories, consider `using virtualenv`_.

.. _using virtualenv: http://blog.mekk.waw.pl/archives/6-Python-VirtualEnv.html

Configuration
--------------

The `~/.calibre-utils` file can be used to configure some program
settings.  The file is created, if missing, whenever any of the
scripts is run, and can be customized.

Here is the default content::

    [commands]
    catdoc = catdoc
    archmage = archmage
    djvutxt = djvutxt
    calibredb = calibredb
    pdftotext = pdftotext
    
    [isbn-search]
    guess_lead_lines = 10000
    guess_lead_pages = 10

The commands section defines location of the external tools being
used.  In case the commands are present in PATH, bare names can be
used. Otherwise full path can be specified. Finally, if some tool is
missing, it can be defined as empty string.

The isbn-search section specifies how many leading pages (in
page-based document formats like PDF or DJVU) or lines (in the free
formats like TXT or CHM) are scanned looking for ISBN-like strings.

For example, the file can be changed so::

    [commands]
    catdoc = /usr/local/bin/catdoc
    archmage = 
    djvutxt = 
    calibredb = /opt/calibre/calibredb
    pdftotext = pdftotext
    
    [isbn-search]
    guess_lead_lines = 12000
    guess_lead_pages = 15

In such a case catdoc will be used from /usr/local/bin, calibredb will
be expected in /opt/calibre, pdftotext will be sought in PATH, and
archmage and djvutxt will be treat as missing (so the isbn guessing
script won't be able to scan CHM and DJVU files for ISBN and will
ignore them).


Sources, bug reports
====================

The project is `hosted here`_.

.. _hosted here: http://bitbucket.org/Mekk/calibre_utils
.. _Calibre: http://calibre-ebook.com/
.. _ootools: http://pypi.python.org/pypi/ootools/0.1dev
