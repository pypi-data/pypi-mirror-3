# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
from setuptools import setup, find_packages

version = '0.2'

deps = []

try:
    import json
except ImportError:
    deps.append('simplejson')

setup(name='datazilla',
      version=version,
      description="Python library to interact with the datazilla server",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Malini Das',
      author_email='mdas@mozilla.com',
      url='https://github.com/mozilla/datazilla_client',
      license='MPL',
      packages=['datazilla'],
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      )
