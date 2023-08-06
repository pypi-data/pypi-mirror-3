"""
setup packaging script for PaInt
"""

import os

version = "0.1.2"
dependencies = ['virtualenv >= 1.7.1.2', 'pip >= 1.1', 'pkginfo', 'CommandParser >= 0.1.3']

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
      [console_scripts]
      python-package = paint.main:main
"""
    kw['install_requires'] = dependencies
except ImportError:
    from distutils.core import setup
    kw['requires'] = dependencies

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''

setup(name='PaInt',
      version=version,
      description="python PAckage INTrospection",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/mozilla/hg/PaInt',
      license='MPL',
      packages=['paint'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
