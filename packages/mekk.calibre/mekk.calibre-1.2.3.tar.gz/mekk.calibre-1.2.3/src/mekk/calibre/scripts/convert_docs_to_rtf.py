# -*- coding: utf-8 -*-

"""
Add .rtf version to all books kept in Calibre_
which have only .doc.

.. _Calibre: http://calibre-ebook.com

Purpose
=======

Calibre does not handle .doc files natively, but it handles .rtf.
So, to make book format conversion possible, this script updates
all .doc books with .rtf alternative.

OpenOffice (and pyuno libraries provided by it) are used in the
process.

Prerequisities
==============

Calibre must be installed and it's programs present in PATH.

Python2.6 must be installed.

ootools library (<http://pypi.python.org/pypi/ootools/0.1dev>) must
be installed. Simplest method to install it:

    easy_install ootools

(on Ubuntu `sudo easy_install ootools`)

Usage
=====

Just open some terminal and run

     calibre_convert_docs_to_rtf

"""

import os
import os.path
from tempfile import NamedTemporaryFile
from collections import namedtuple

from mekk.calibre.calibre_util import \
    find_calibre_books, add_format_to_calibre

from mekk.calibre.openoffice import doc2rtf_converter

############################################################
# Operations
############################################################

DocItem = namedtuple('DocItem', 'id uuid title file')


def locate_docs_without_rtf():
    """
    Locates all files which have .doc but do not have .rtf version

    Routine yields objects with fields:
       id,
       uuid,
       title
       file (.doc file name)
    """
    for book in find_calibre_books(search="format:doc and not format:rtf"):
        files = [f
                 for f in book.files
                 if f.lower().endswith('.doc')]
        if files:
            yield DocItem(id=book.id,
                          uuid=book.uuid,
                          title=book.title,
                          file=files[0])


def make_rtf_for(item):
    """
    Call doc2rtf converter to create .rtf file for given item.
    Item is a standard object (item.id is a calibre id, item.file is .doc)
    """
    rtf_file = NamedTemporaryFile(suffix=".rtf", delete=False)
    rtf_name = rtf_file.name
    print "Creating RTF for book %s (%s) in %s" % (
        item.id, item.title, rtf_name)
    try:
        rtf_file.close()
        doc2rtf_converter.convert(item.file, rtf_name)
        add_format_to_calibre(item.id, rtf_name)
    finally:
        os.remove(rtf_name)

############################################################
# Main
############################################################


def run():
    """
    Run calibre_convert_docs_to_rtf script
    """
    for doc_file in locate_docs_without_rtf():
        make_rtf_for(doc_file)
