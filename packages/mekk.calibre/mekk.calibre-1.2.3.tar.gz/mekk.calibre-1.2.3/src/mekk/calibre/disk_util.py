# -*- coding: utf-8 -*-

import os.path
import os
import filecmp

def dir_depth(root_dir, checked_dir):
    """
    Calculates directory depth (= level of subdirectory belonging) of checked_dir under root_dir.
    For example:

    >>> dir_depth("/some/dir", "/some/dir")
    0
    >>> dir_depth("/some/dir", "/some/dir/subdir")
    1
    >>> dir_depth("/some/dir", "/some/dir/subdir/another/yet_another")
    3
    >>> dir_depth("/some/dir", "/some/other/dir")
    Traceback...
    Exception: Directory /some is not subdirectory of /some/dir
    """
    if len(root_dir) >= len(checked_dir):
        if root_dir == checked_dir:
            return 0
        else:
            raise Exception("Directory %s is not subdirectory of %s" % (checked_dir, root_dir))
    lead, rest = os.path.split(checked_dir)
    return 1 + dir_depth(root_dir, lead)

def find_disk_files(root,
                    ignored_names=("metadata.db", "metadata.opf"),
                    ignored_extensions=(".jpg", ".gif"),
                    min_level = 0,
                    max_level = 9999999):
    """
    Locates and returns all disk files under directory root, ignoring
    those unnecessary. Yields all files found (full names).

    root - the root directory for files beeing looked up
    ignored_names - the list of (short) filenames to ignore
    ignored_extensions - the list of file extensions (suffixes) to ignore
    min_level - minimum count of directories between root and file (0 means any file, 1 skips top-level files, etc)
    max_level - maximum count of directories between root and file
    """
    for dirname, subdirs, files in os.walk(root, topdown = True):
        depth = dir_depth(root, dirname)
        if depth == max_level:
            subdirs[:] = []
        if depth < min_level:
            pass
        elif depth <= max_level:
            for short_name in files:
                if short_name in ignored_names:
                    continue
                if any(short_name.endswith(ext) for ext in ignored_extensions):
                    continue
                full_name = os.path.join(dirname, short_name)
                yield full_name

def file_size(filename):
    """
    Returns file size in bytes
    """
    stat = os.stat(filename)
    return stat.st_size


def file_extension(file_path):
    """
    Returns bare extension for given file. The extension starts with .
    and is always lowercase - so example return values are ".pdf" or ".doc".
    """
    return os.path.splitext(file_path)[1].lower()


def are_files_identical(filename1, filename2):
    return filecmp.cmp(filename1, filename2, False)
