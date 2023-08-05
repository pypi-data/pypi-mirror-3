# -*- coding: utf-8 -*-

"""
Routines directly related to Sony PRS-600 (and, maybe, similar devices)
"""

"""
Commands being used
===================

ebook-device ls
---------------

The command::

    ebook-device ls -lR /

prints recursively all files on the device, for example::

    /media/READER/:
    drwxrwxrwx   8192 2009-01-18 00:36 Documents
    drwxrwxrwx   8192 2010-02-23 21:37 database
    drwxrwxrwx   8192 2009-12-02 20:44 tmp
    drwxrwxrwx   8192 2010-02-23 23:38 Digital Editions
    -rw-rw-rw- 170593 2010-06-24 20:11 metadata.calibre
    drwxrwxrwx   8192 2010-02-25 23:45 FONT
    
    /media/READER/Documents:
    -rw-rw-rw-   167099 2009-01-02 04:00 LICENSE.zip
    -rw-rw-rw- 23760190 2009-02-22 19:00 PRS600_UG.zip
    
    /media/READER/database:
    drwxrwxrwx 8192 2010-02-23 21:32 sync
    drwxrwxrwx 8192 2010-02-23 13:23 media
    drwxrwxrwx 8192 2010-07-16 22:03 cache
    drwxrwxrwx 8192 2009-06-12 22:45 layout
    drwxrwxrwx 8192 2010-02-23 21:37 markup
    
    /media/READER/database/sync:
    -rw-rw-rw- 2958 2010-07-11 21:14 deleted.xml
    -rw-rw-rw- 4764 2009-12-02 13:38 cache2.xml

    (...)

On Sony PRS-600 annotations and notes can be found in the following places::

    /media/READER/database/media/notepads:
    -rw-rw-rw-  9494 2010-03-10 01:59 1266935008146.086.note
    -rw-rw-rw-  4444 2010-04-04 20:54 1270414440779.731.note
    -rw-rw-rw-  8203 2010-04-12 20:31 1271104072104.857.note
    -rw-rw-rw- 12064 2010-07-11 21:16 1278882857756.752.note
    (...)

(free notes)

    /media/READER/database/markup/database/media/books:
    drwxrwxrwx 8192 2010-02-26 17:58 Harper, Robert
    drwxrwxrwx 8192 2010-02-27 07:42 Adams, Cameron
    drwxrwxrwx 8192 2010-02-27 20:49 Unknown
    drwxrwxrwx 8192 2010-03-27 20:30 Lesmian, Boleslaw
    drwxrwxrwx 8192 2010-07-11 21:10 John Allspaw
    (...)

    /media/READER/database/markup/database/media/books/Harper, Robert:
    drwxrwxrwx 8192 2010-02-26 17:58 Programming in Standard ML - Robert Harper.pdf

    /media/READER/database/markup/database/media/books/Lesmian, Boleslaw/Basn o pieknej Parysadzie i o Ptaku Bulbulezarze - Boleslaw Lesmian.epub:
    -rw-rw-rw-  459 2010-03-27 20:35 1269725457096.839.svg
    -rw-rw-rw- 5612 2010-03-27 20:35 1269725457096.839.jpg

    /media/READER/database/markup/database/media/books/John Allspaw:
    drwxrwxrwx 8192 2010-07-11 21:18 Web Operations_ Keeping the Data on Time - John Allspaw & Jesse Robbins_3977.epub
    
    /media/READER/database/markup/database/media/books/John Allspaw/Web Operations_ Keeping the Data on Time - John Allspaw & Jesse Robbins_3977.epub:
    -rw-rw-rw-   947 2010-07-11 21:18 1278882605468.228.svg
    -rw-rw-rw-  6413 2010-07-11 21:18 1278882605468.228.jpg
    -rw-rw-rw- 20760 2010-07-11 21:13 1278882712195.683.svg
    -rw-rw-rw-  6675 2010-07-11 21:13 1278882712195.683.jpg

(graphical, always pair .svg and .jpg, many such pairs can be present for one book)

    /media/READER/Digital Editions/Annotations/database/media/books/Harper, Robert:
    -rw-rw-rw- 345 2010-02-27 23:01 Programming in Standard ML - Robert Harper.pdf.annot

    /media/READER/Digital Editions/Annotations/database/media/books/Adams, Cameron:
    -rw-rw-rw- 946 2010-03-30 17:50 The Art & Science Of JavaScript - Cameron Adams.pdf.annot

(markers in xml, single file per book, one dir can contain many .annot
files if there are many books by one author and all are annotated)

"""

def detect_mountpoint():
    """
    Attempts to guess the mount point for the connected device
    """
    raise NotImplementedError
    

def find_annotations(mount_point):
    """
    Iterates over all annotations found on the device. For every
    annotation found yields full path (including mount point)
    
    """
    raise NotImplementedError

