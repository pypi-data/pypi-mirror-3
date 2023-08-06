"""
setup packaging script for FileServer
"""

import os

version = "0.1"
dependencies = ['webob']

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
      [console_scripts]
      FileServer = FileServer.main:main
      FileServer-template = FileServer.template:main
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


setup(name='FileServer',
      version=version,
      description="a simple static fileserver and directory index server in python (WSGI app)",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/hg/FileServer',
      license='',
      packages=['fileserver'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
