#!/usr/bin/env python
#-*- coding: utf-8 -*-

from distutils.core import setup, Extension
import sys

## patch distutils for added setup keywords for Python versions < 2.2.3...
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

## enable 'build_sphinx' command if Sphinx is installed...
cmdclass = {}
try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    import warnings
    warnings.formatwarning = lambda *a: ' ** WARNING: %s\n' % a[0]
    msg = "no Sphinx install found, 'build_sphinx' command disabled."
    warnings.warn(msg, RuntimeWarning)

setup(name='draxoft.pkginfo',
      version='0.1',
      author='Ryan Volpe',
      author_email='ryan@draxoft.com',
      description='',
      url='http://packages.python.org/draxoft.pkginfo',
      download_url='http://pypi.python.org/pypi/draxoft.pkginfo/0.1',
      package_dir={'': 'src'},
      cmdclass=cmdclass,
      # py_modules=[],
      packages=['draxoft', 'draxoft.tools'],
      # ext_modules=[],
      scripts=['pkginfo.py'],
      # requires=[],
      # provides=[],
      # obsoletes=[],
      classifiers=['Programming Language :: Python',
                   'Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'License :: Other/Proprietary License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Build Tools',
                   'Topic :: System :: Software Distribution',
                   'Topic :: Utilities'],
      long_description=''''''
     )
