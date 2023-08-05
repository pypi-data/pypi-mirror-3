# -*- coding: utf-8 -*-

"""OpenOffice interface"""

import ootools
import uno
import os
import os.path

# Workaround for a bug in ootools
from com.sun.star.beans import PropertyValue
ootools.PropertyValue = PropertyValue

## TODO: rozważyć przejście na unoconv


class Doc2RtfConverter(object):
    """
    Wrapper for openoffice interface used to convert .doc to .rtf.
    Once created, the object can be used to perform many conversions
    (and should be used this way as initialization is costly).
    """

    def __init__(self):
        self.runner = None
        self.desktop = None

    def convert(self, input_file, output_file):
        """
        Perform actual conversion, make output_file (.rtf) from
        input_file (.doc).
        """
        self._ensure_active()
        input_url = uno.systemPathToFileUrl(os.path.abspath(input_file))
        output_url = uno.systemPathToFileUrl(os.path.abspath(output_file))
        props = ootools.oo_properties(FilterName="Rich Text Format")
        #desktop = self.runner.connect()
        document = self.desktop.loadComponentFromURL(
            input_url, "_blank", 0, ootools.oo_properties())
        if not document:
            raise Exception(
                "Can't load document (wrong doc?) from %s" % input_file)
        try:
            document.storeToURL(output_url, props)
        finally:
            document.close(True)

    def _ensure_active(self):
        """
        Start OpenOffice if not yest started
        """
        if not self.runner:
            print "Starting up OpenOffice"
            self.runner = ootools.OORunner()
            self.runner.start()
            self.desktop = self.runner.connect()

    def __del__(self):
        if self.runner:
            print "Shutting down OpenOffice"
            self.runner.stop()


doc2rtf_converter = Doc2RtfConverter()


#where = "%s/tmp" % os.environ['HOME']
#doc2rtf_converter.convert(os.path.join(where, "test.doc"),
#                  os.path.join(where, "test.rtf"))
