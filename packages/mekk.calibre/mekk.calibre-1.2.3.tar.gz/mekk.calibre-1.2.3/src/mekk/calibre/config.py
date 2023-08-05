# -*- coding: utf-8 -*-

"""
Configuration defaults and handling
"""

import ConfigParser
import os.path

CONFIG_LOCATION = "~/.calibre-utils"


class Config(object):
    """
    Wrapper for configuration settings
    """

    # Command names for external programs

    calibredb = "calibredb"
    pdftotext = "pdftotext"
    catdoc = "catdoc"
    djvutxt = "djvutxt"
    archmage = "archmage"
    ebook_device = "ebook-device"

    # How many pages to scan looking for ISBN - in page-based docs
    guess_lead_pages = 10
    # How many lines to scan looking for ISBN - in non-paged docs
    guess_lead_lines = 10000

    # Every that many files progress note is shown
    progress_report_every = 50

    def __init__(self, inifile=CONFIG_LOCATION):
        """
        Loads params from given config file, creates the file if missing,
        adds missing params to file if not all are present.
        """

        # .ini section naming
        commands_section = "commands"
        isbn_section = "isbn-search"

        config = ConfigParser.SafeConfigParser({})

        ini = os.path.abspath(os.path.expanduser(inifile))
        if os.path.exists(ini):
            config.read(ini)

        for section in [commands_section, isbn_section]:
            if not config.has_section(section):
                config.add_section(section)

        config_changed = False

        for cmdopt in ["calibredb",
                       "ebook_device",
                       "pdftotext",
                       "catdoc",
                       "djvutxt",
                       "archmage"]:
            if config.has_option(commands_section, cmdopt):
                setattr(self, cmdopt, config.get(commands_section, cmdopt))
            else:
                config_changed = True
                config.set(commands_section, cmdopt, getattr(self, cmdopt))

        for cmdopt in ["guess_lead_pages", "guess_lead_lines"]:
            if config.has_option(isbn_section, cmdopt):
                setattr(self, cmdopt, config.getint(isbn_section, cmdopt))
            else:
                config_changed = True
                config.set(isbn_section, cmdopt, str(getattr(self, cmdopt)))

        if config_changed:
            config.write(open(ini, 'w'))


_CONFIG = None


def standard_config():
    """
    Return configuration singleton.

    It's a function (instead of global variable) to avoid parsing .ini
    if it is not used (for example - during tests).
    """
    global _CONFIG
    if not _CONFIG:
        _CONFIG = Config()
    return _CONFIG

# TODO: report missing tools and suggest how to install them
