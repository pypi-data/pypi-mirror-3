# -*- coding: utf-8 -*-

"""
ISBN extractint routine (and regexp)
"""

import re

############################################################
# Extracting ISBN from book text
############################################################

RE_ISBN = re.compile(u"(?:ISBN[-– ]*(?:|10|13)|International Standard Book Number)[:\s]*(?:|, PDF ed.|, print ed.|\(pbk\)|\(electronic\))[:\s]*([-\-–0-9Xx]{10,25})",
                     re.MULTILINE + re.UNICODE)

def verify_isbn_checksum(isbn):
    """
    Checks whether given ISBN (can be 10- or 13- digit) has proper checksum.
    Returns true if the sum is proper, false otherwise.
    """
    if len(isbn) == 10:
        digits = [(d in ['x', 'X']) and 10 or int(d) for d in isbn]
        t, s = 0, 0
        for d in digits:
            t = t + d
            s = s + t
        ctrlsum = s % 11
        return ctrlsum == 0
    elif len(isbn) == 13:
        # Prefix is only 978 or 979 for books, see http://www.isbn-international.org/faqs/view/5#q_5
        pfx = isbn[:3]
        if pfx not in ["978", "979"]: 
            return False
        # Actual checksum verification
        digits = [(d in ['x', 'X']) and 10 or int(d) for d in isbn]
        ctrlsum = (sum(digits[::2]) + 3 * sum(digits[1::2])) % 10
        return ctrlsum == 0
    else:
        return False

def look_for_isbn_in_text(text):
    """
    Scans text (string) for ISBN, returns one if found
    """
    isbns10 = []
    isbns13 = []
    for match in RE_ISBN.finditer(text):
        txt = match.group(1)
        txt = txt.replace("-", "")
        txt_len = len(txt)
        if txt_len == 10:
            if verify_isbn_checksum(txt):
                isbns10.append(txt)
        elif txt_len == 13:
            if verify_isbn_checksum(txt):
                isbns13.append(txt)
    # TODO: more sophisticated choice if there are many isbn's
    if isbns13:
        return isbns13[0]
    elif isbns10:
        return isbns10[0]
    else:
        return None
