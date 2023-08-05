# -*- coding: utf-8 -*-

"""
Text extraction routines
"""

# TODO: differentiate partial and full extract (and handle the latter too)

import subprocess
import os
from lxml import etree, html
from mekk.calibre.disk_util import file_extension
from mekk.calibre.config import standard_config, CONFIG_LOCATION

CONFIG = standard_config()

############################################################
# Extracting leading pages of the book from different
# formats
############################################################

text_extractors = dict()


def grab_file_text_pdf(file_path):
    """
    Extract leading text from .pdf file
    """
    try:
        txt = subprocess.Popen(
            [CONFIG.pdftotext, file_path,
              "-f", "1", "-l", str(CONFIG.guess_lead_pages), "-"],
            stdout=subprocess.PIPE,
            stderr=open(os.devnull, 'w'),
            ).communicate()[0]
        return txt
    except OSError, error:
        if error.errno == 2:
            raise Exception(
                """pdftotext (configured as %s) not found.
Install poppler-utils, or edit %s to configure
path to pdftotext (or to disable this tool)""" \
                    % (CONFIG.pdftotext, CONFIG_LOCATION))
        else:
            raise


if CONFIG.pdftotext:
    text_extractors[".pdf"] = grab_file_text_pdf


def grab_file_text_txt(file_path):
    """
    Extract leading text from .txt file
    """
    file_obj = open(file_path, "r")
    txt = "".join(file_obj.readlines(CONFIG.guess_lead_lines))
    return txt


text_extractors[".txt"] = grab_file_text_txt


def grab_file_text_catdoc(file_path):
    """
    Extract leading text from .doc or .rtf (catdoc-known file)
    """
    try:
        txt = subprocess.Popen(
            [CONFIG.catdoc, file_path],
            stdout=subprocess.PIPE,
            stderr=open(os.devnull, 'w'),
            ).communicate()[0]
        return txt
    except OSError, err:
        if err.errno == 2:
            raise Exception(
                """catdoc (configured as %s) not found.
Install poppler-utils, or edit %s to disable catdoc or to set path to it.""" %
                            (CONFIG.catdoc, CONFIG_LOCATION))
        else:
            raise


if CONFIG.catdoc:
    text_extractors[".rtf"] = grab_file_text_catdoc
    text_extractors[".doc"] = grab_file_text_catdoc


def grab_file_text_djvu(file_path):
    """
    Extract leading text from .djvu file
    """
    try:
        txt = subprocess.Popen(
            [CONFIG.djvutxt,
             "-page=0-%d" % CONFIG.guess_lead_pages,
             file_path],
            stdout=subprocess.PIPE,
            stderr=open(os.devnull, 'w'),
            ).communicate()[0]
        return txt
    except OSError, err:
        if err.errno == 2:
            raise Exception(
                """djvutxt (configured as %s) not found.
Install djvulibre-bin, or edit %s to disable djvutxt or to set path to it.""" %
                (CONFIG.djvutxt, CONFIG_LOCATION))
        else:
            raise


if CONFIG.djvutxt:
    text_extractors[".djvu"] = grab_file_text_djvu


def grab_file_text_chm(file_path):
    """
    Extract leading text from .chm file
    """
    try:
        pipe = subprocess.Popen(
            [CONFIG.archmage, "--dump", file_path],
            stdout=subprocess.PIPE,
            stderr=open(os.devnull, 'w'),
            )
    except OSError, err:
        if err.errno == 2:
            raise Exception(
                """archmage (configured as %s) not found.
Install archmage, or edit %s to disable it or to set proper path to it.""" %
                (CONFIG.archmage, CONFIG_LOCATION))
        else:
            raise
    lines = []
    for line in pipe.stdout:
        if line.strip():
            lines.append(line)
            if len(lines) > CONFIG.guess_lead_lines:
                break
    pipe.terminate()
    doc_text = "".join(lines)
    try:
        return "\n".join(html.fromstring(doc_text).itertext()).encode("utf-8")
    except etree.XMLSyntaxError:
        print "Problems parsing content of", file_path
        return doc_text.encode("utf-8")
    except UnicodeDecodeError:
        # fallback, see https://bitbucket.org/Mekk/calibre_utils/issue/3/unicodedecodeerror-in-text_extractpy
        return unicode(doc_text, "latin-1", "ignore") 

if CONFIG.archmage:
    text_extractors[".chm"] = grab_file_text_chm

############################################################
# Wrapper for extractor routines
############################################################


def grab_file_text_for_analysis(file_path):
    """
    Grabs a couple of leading pages from given file, returns them as text
    """
    format = file_extension(file_path)

    routine = text_extractors.get(format)

    if routine:
        return routine(file_path)
    else:
        raise Exception("Unknown format: %s" % format)


def can_extract_text_from(file_path):
    """
    Preliminary (extension-based) test whether given file can work
    """
    return file_extension(file_path) in text_extractors
