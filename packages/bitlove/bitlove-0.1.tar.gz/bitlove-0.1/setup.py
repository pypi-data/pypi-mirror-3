#!/usr/bin/env python
# Setup script for bitlove-python

from distutils.core import setup

import re


src = open('bitlove.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", src))
docstrings = re.findall('"""(.*)"""', src)

PACKAGE = 'bitlove'

# Metadata fields extracted from source file
AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
WEBSITE = metadata['website']
LICENSE = metadata['license']
DESCRIPTION = docstrings[0].strip()
if '\n\n' in DESCRIPTION:
    DESCRIPTION, LONG_DESCRIPTION = DESCRIPTION.split('\n\n', 1)
else:
    LONG_DESCRIPTION = None

# Extract name and e-mail ("Firstname Lastname <mail@example.org>")
AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

setup(name=PACKAGE,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=WEBSITE,
      download_url='http://pypi.python.org/packages/source/' + \
        PACKAGE[0] + '/' + PACKAGE + '/' + \
        PACKAGE + '-' + VERSION + '.tar.gz')
