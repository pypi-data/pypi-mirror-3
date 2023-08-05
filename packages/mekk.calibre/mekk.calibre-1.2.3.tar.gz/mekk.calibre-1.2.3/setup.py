# -*- coding: utf-8 -*-
# (c) 2010, Marcin Kasperski

from setuptools import setup, find_packages

VERSION = '1.2.3'
DESCRIPTION = "Calibre helper scripts (ISBN guessing, RTF to DOC conversion," \
    + "hanging books detection, ...)."
LONG_DESCRIPTION = open("README.txt").read()
CLASSIFIERS = [
    "Programming Language :: Python",
    "Intended Audience :: End Users/Desktop",
    "Topic :: Utilities", # Topic :: Text Processing"
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    # "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 2",
    ]

setup(name='mekk.calibre',
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      classifiers=CLASSIFIERS,
      keywords='org',
      license='BSD',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://mekk.waw.pl/',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite='nose.collector',
      include_package_data=True,
      package_data={
        'mekk': [
            'README.txt',
            'LICENSE.txt',
            'doc/usage.txt',
            ],
        },
      zip_safe=True,
      install_requires=[
        'lxml',
      ],
      extras_require=dict(
        docs2rtf=['ootools'],
        ),
      tests_require=[
        'nose',
        ],
      entry_points="""
[console_scripts]
calibre_find_books_missing_in_database = mekk.calibre.scripts.find_books_missing_in_database:run
calibre_guess_and_add_isbn = mekk.calibre.scripts.guess_and_add_isbn:run
calibre_convert_docs_to_rtf = mekk.calibre.scripts.convert_docs_to_rtf:run
calibre_add_if_missing = mekk.calibre.scripts.add_if_missing:run
calibre_report_duplicates = mekk.calibre.scripts.report_duplicates:run
""",
)
