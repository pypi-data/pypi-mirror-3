# -*- coding: utf-8 -*-

"""
Looking up files which are present on disk, but are
missing in Calibre database (inconsistencies).

The files are reported to standard output. To add them
all to calibre, pipe output. For example:

 python find_books_missing_in_database.py | xargs -d "\n" calibredb add

(but, better, review everything beforehand)
"""

import os.path
import sys
from mekk.calibre.calibre_util import find_calibre_file_names
from mekk.calibre.disk_util import find_disk_files

############################################################
# Main
############################################################


def run():
    """
    Run calibre_find_books_missing_in_database script
    """
    known_by_calibre = set()

    for file_name in find_calibre_file_names():
        known_by_calibre.add(file_name)

    root = os.path.dirname(os.path.dirname(os.path.dirname(file_name)))

    correct_count = 0
    missing_count = 0
    for file_name in find_disk_files(root, min_level = 2, max_level = 2,
                                     ignored_names=["metadata.opf", "cover.jpg", "cover.png"],
                                     ignored_extensions = ["~", ".jpg", ".gif"]):
        if not file_name in known_by_calibre:
            print file_name
            missing_count += 1
        else:
            correct_count += 1

    print >> sys.stderr, "%d files properly managed by calibre" % correct_count
    if missing_count:
        print >> sys.stderr, "%d files unknown" % missing_count
