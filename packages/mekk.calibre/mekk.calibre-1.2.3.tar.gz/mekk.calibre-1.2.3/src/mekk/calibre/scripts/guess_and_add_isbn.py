# -*- coding: utf-8 -*-

"""
Autodetect ISBN for books kept inside
Calibre <http://calibre-ebook.com/> database.

Purpose
=======

The script is analysing calibre database (it assumes calibre is
already installed and properly configured), looking for books without
ISBN, then tries to find their ISBN (by scanning leading pages for
it). If ISBN is found, it updates given book metatada with it.

Later on ISBN can be used to grab the book metatada and/or book cover
inside Calibre GUI. Just spawn Calibre and look for books with ISBN
set and missing metadata, for example using query like:

     isbn:~[0-9] not publisher:~[a-z]

(above means: isbn contains some digit, publisher does not contain any
letter), mark them, right click, expand Edit Medatada Information
submenu and pick Download Metadata (or some other Download option).

Prerequisities
==============

Calibre must be installed, properly configured and has
some database (otherwise it does not make sense to run the script).
The
    calibredb
command must be in PATH (or CALIBREDB variable below can be modified
to show full path of it).

Tools providing commands
    pdftotext
    catdoc
    djvutxt
    archmage
must be installed and present in PATH. On Ubuntu Linux or Debian Linux
those can be installed from standard repositories, just install the
following packages
    poppler-utils
    catdoc
    djvulibre-bin
    archmage

Python 2.6 is required (script is using features of tempfile and
subprocess introduced in 2.6). Also, lxml library must be installed.
On Debian or Ubuntu just install the following packages:
   python2.6
   python-lxml

I use this script on Ubuntu Linux. The script as such should work on
Windows or Mac if necessary tools are installed, but I've never tried
it.

Usage
=====

Spawn terminal or console, check whether PATH contains calibredb,
pdftotext, catdoc and djvutxt, then just run

   calibre_guess_and_add_isbn

and wait for the script to finish.

Note: it may take some time, especially on bigger databases.

Extra notes
===========

The script can be run while Calibre is running (it will notify
running Calibre about data changes).

Development
===========

Sources are tracked on http://bitbucket.org/Mekk/calibre_utils

"""

from collections import namedtuple
from mekk.calibre.calibre_util import  \
    find_calibre_books, save_isbn
from mekk.calibre.text_extract import \
    grab_file_text_for_analysis, can_extract_text_from
from mekk.calibre.isbn import look_for_isbn_in_text
from mekk.calibre.config import standard_config
import traceback

CONFIG = standard_config()
ERROR_LIMIT = 10

############################################################
# Locating files for analysis
############################################################

IsbnItem = namedtuple('IsbnItem', 'id uuid title files')


def locate_potential_isbn_files():
    """
    Locates all files which may be used for ISBN grabbing.
    The file is returned if:
    - it does not have metadata ISBN set
    - it has one of the known formats (pdf, rtf, djvu, txt, chm - what
      extractors handle)

    Routine yields objects with fields:
       id,
       uuid,
       title
       files  (list of all possibly suitable files, at least one item)
    """
    checked_count = 0
    for item_no, book in enumerate(find_calibre_books()): # TODO: search
        if not book.isbn:
            files = [f
                     for f in book.files
                     if can_extract_text_from(f)]
            if files:
                checked_count += 1
                yield IsbnItem(id=book.id,
                               uuid=book.uuid,
                               title=book.title,
                               files=files)
        if item_no > 0 and item_no % CONFIG.progress_report_every == 0:
            print "Info: %d files found, %d checked" % (item_no, checked_count)


def find_files_with_new_isbn():
    """
    Checks files for ISBN. Yields all files for which it was found,
    as pairs: item, isbn (where item is the same as above)
    """
    error_count = 0
    for item in locate_potential_isbn_files():
        try:
            candid = set()
            for file_name in item.files:
                txt = grab_file_text_for_analysis(file_name)
                isbn = look_for_isbn_in_text(txt)
                if isbn:
                    candid.add(isbn)
            if len(candid) == 1:
                isbn = candid.pop()
                yield item, isbn
            elif len(candid) > 1:
                raise Exception(
                    "ISBN conflict in %s: %s" % (str(item), str(candid)))
        except KeyboardInterrupt:
            print "Ctrl-C pressed, stopping"
            break
        except: #  Exception as e:
            error_count += 1
            print "Exception while handling book '%s'. Details:" % (
                item.title)
            traceback.print_exc()
            print
            if error_count > ERROR_LIMIT:
                print "Too many errors (%d) happened. Stopping" % error_count
                break

############################################################
# Main
############################################################


def run():
    """
    Run calibre_guess_and_add_isbn script
    """
    for item, isbn in find_files_with_new_isbn():
        save_isbn(item, isbn)
