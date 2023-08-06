#!/usr/bin/env python
# Setup script for python-decontractors
# by Thomas Perl <thp.io/about>

from distutils.core import setup

import re

decontractors_py = open('decontractors.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", decontractors_py))
docstrings = re.findall('"""(.*)"""', decontractors_py)

# How is the package going to be called?
PACKAGE = 'decontractors'

# List the modules that need to be installed/packaged
MODULES = (
        'decontractors',
)

# Metadata fields extracted from decontractors.py
AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
WEBSITE = metadata['website']
LICENSE = metadata['license']
DESCRIPTION = docstrings[0]

# Extract name and e-mail ("Firstname Lastname <mail@example.org>")
AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

setup(name=PACKAGE,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=WEBSITE,
      py_modules=MODULES,
      download_url=WEBSITE+PACKAGE+'-'+VERSION+'.tar.gz')

