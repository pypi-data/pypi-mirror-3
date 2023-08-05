# -*- coding: utf-8 -*-

"""
Scans given directory, adds to calibre all books which are not yet
present there. Duplicate checking is done solely on file content
comparison (file name may differ).  Used to double-check whether some
dir items were added to calibre, or not fully.

Example:

    calibre_add_if_missing /home/jan/OldBooks

(and later remove OldBooks if everything is OK).

Can be also used to add individual files, for example:

    calibre_add_if_missing *.pdf *.djvu subdir/*.pdf

"""

import sys
import os.path
from collections import defaultdict
from mekk.calibre.calibre_util import \
    find_calibre_file_names, add_to_calibre
from mekk.calibre.disk_util import \
    find_disk_files, file_size, are_files_identical


def run():
    """
    Run calibre_add_if_missing script
    """
    if len(sys.argv) < 2:
        print "Execute with:"
        print "    calibre_add_if_missing  /some/dire/ctory/name"
        print "or"
        print "    calibre_add_if_missing  file.name otherfile.name dir.name"
        sys.exit(1)

    files_to_check = []
    for param in sys.argv[1:]:
        if os.path.isdir(param):
            files_to_check.extend(find_disk_files(param))
        else:
            files_to_check.append(param)

    # size -> set of files with that size
    known_by_calibre = defaultdict(lambda: set())

    for file_name in find_calibre_file_names():
        known_by_calibre[file_size(file_name)].add(file_name)

    added_count = 0
    skipped_count = 0
    for file_name in files_to_check:
        candidates = known_by_calibre[file_size(file_name)]
        for c in candidates:
            if are_files_identical(file_name, c):
                print "Already present: %s (stored as %s)" % (file_name, c)
                skipped_count += 1
                break
        else:
            print "Not registered by calibre:", file_name
            add_to_calibre(file_name)
            added_count += 1

    print
    print "%d files already present, %d added" % (skipped_count, added_count)
