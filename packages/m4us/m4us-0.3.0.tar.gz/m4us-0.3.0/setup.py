#/usr/bin/env python
# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2009-2012 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.

"""Installation and distribution creation script for m4us."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
import codecs
from os import path

#---  Third-party imports

#---  Project imports


#---Globals--------------------------------------------------------------------

NAME = 'm4us'
VERSION = '0.3.0'

HERE = path.abspath(path.dirname(__file__))
README = codecs.open(path.join(HERE, 'README'), encoding='utf-8').read()

# List your project dependencies here.
# For more details, see:
# http://packages.python.org/distribute/setuptools.html#declaring-dependencies
# Note: Dependency versions are specified in parentheses as per PEP314 and
# PEP345.  They will be adjusted automatically to comply with distribute/
# setuptools install_requires convention.
REQUIRES = [
  'zope.interface (>=3.8.0,<3.8.99)',
  'decorator (>=3.3.2,<3.3.99)',
  # Test dependencies.  The tests can be run anywhere.
  'unittest2 (>=0.5.1,<0.5.99)',
  'mock (>=0.8.0,<0.8.99)',
  # Sub-dependencies
  # (none)
]


#---Functions------------------------------------------------------------------

def requires_to_install_requires(requires):
    install_requires = []
    for requirement in requires:
        for character in ' ()':
            requirement = requirement.replace(character, '')
        install_requires.append(requirement)
    return install_requires


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

try:
    import setuptools
    if not hasattr(setuptools, '_distribute'):
        import warnings
        warnings.warn(
          'Use of setuptools is deprecated.  Use distribute instead.',
          DeprecationWarning,
        )
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()


#---Late Imports---------------------------------------------------------------

#---  Third-party imports
import setuptools


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

setuptools.setup(
  # PEP241 fields:
  name=NAME,
  version=VERSION,
  description=('A pythonic coroutine-based concurrent programming framework '
    'inspired by Kamaelia.'),
  long_description=README,
  keywords='m4us concurrency coroutine kamaelia framework message',
  url='http://pypi.python.org/pypi/m4us',
  author='Krys Lawrence',
  # Not using a mailing list yet.
  ##author_email='everyapp.bootstrap@googlegroups.com',
  author_email='m4us@krys.ca',

  # PEP314 fields:
  ##platform=[],
  ##license='',
  download_url='http://pypi.python.org/pypi/m4us#downloads',
  # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers=[
      ##'Development Status :: 1 - Planning',
      ##'Development Status :: 2 - Pre-Alpha',
      'Development Status :: 3 - Alpha',
      ##'Development Status :: 4 - Beta',
      ##'Development Status :: 5 - Production/Stable',
      ##'Development Status :: 6 - Mature',
      ##'Development Status :: 7 - Inactive',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2 :: Only',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
   ],
  requires=REQUIRES,
  provides=[NAME],
  ##obsoletes=[],

  # PEP345 fields:
  # Not yet supported by any installer tool.

  # distutils-specific keys:
  packages=setuptools.find_packages(),
  ##package_dir={},
  ##py_modules=[],
  ##ext_package='',
  ##ext_modules=[],
  ##scripts=[],
  ##package_data={},
  ##data_files=[],
  ##maintainer='',
  ##maintainer_email='',

  # distribute-specific keys:
  ##include_package_data=True,
  ##exclude_package_data={},
  zip_safe=False,
  install_requires=requires_to_install_requires(REQUIRES),
  ##entry_points={},
  ##extras_require={},
  ##setup_requires=[],
  ##dependency_links=[],
  ##namespace_packages=[],
  test_suite='unittest2.collector',
  ##tests_require=[],
  ##test_loader='',
  ##eager_resources=[],
  ##use_2to3=False,
  ##convert_2to3_doctests=False,
  ##use_2to3_fixers=[],
)
