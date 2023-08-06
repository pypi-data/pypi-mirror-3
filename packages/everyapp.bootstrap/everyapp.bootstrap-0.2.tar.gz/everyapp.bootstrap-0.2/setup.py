#/usr/bin/env python
# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of everyapp.bootstrap.
# Copyright (C) 2010-2012 Krys Lawrence
#
# everyapp.bootstrap is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# everyapp.bootstrap is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Installation and distribution creation script for everyapp.bootstrap."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
import codecs
from os import path

#---  Third-party imports

#---  Project imports


#---Globals--------------------------------------------------------------------

NAME = 'everyapp.bootstrap'
VERSION = '0.2'

HERE = path.abspath(path.dirname(__file__))
README = codecs.open(path.join(HERE, 'README.txt'), encoding='utf-8').read()

# List your project dependencies here.
# For more details, see:
# http://packages.python.org/distribute/setuptools.html#declaring-dependencies
# Note: Dependency versions are specified in parentheses as per PEP314 and
# PEP345.  They will be adjusted automatically to comply with distribute/
# setuptools install_requires convention.
REQUIRES = [
  'distribute (>=0.6.24,<0.6.99)',
  'virtualenv (>=1.7.1,<1.7.99)',
  'pip (>=1.1,<1.1.99)',
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
  description='Enhanced virtualenv bootstrap script creation.',
  long_description=README,
  keywords='virtualenv bootstrap everyapp',
  url='http://pypi.python.org/pypi/everyapp.bootstrap',
  author='Krys Lawrence',
  # Not using a mailing list yet.
  ##author_email='everyapp.bootstrap@googlegroups.com',
  author_email='everyapp@krys.ca',

  # PEP314 fields:
  ##platform=[],
  # Strictly speaking, license should not specified, but the Trove classifier
  # for GPL does not let me indicate the GPL version, so I have included it
  # here.
  license='GPLv3+',
  download_url='http://pypi.python.org/pypi/everyapp.bootstrap#downloads',
  # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers=[
    ##'Development Status :: 1 - Planning',
    ##'Development Status :: 2 - Pre-Alpha',
    'Development Status :: 3 - Alpha',
    ##'Development Status :: 4 - Beta',
    ##'Development Status :: 5 - Production/Stable',
    ##'Development Status :: 6 - Mature',
    ##'Development Status :: 7 - Inactive',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    ##'Programming Language :: Python :: 2.3',
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Software Development :: Code Generators',
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
  package_data={'everyapp.bootstrap': ['bootstrap.cfg']},
  ##data_files=[],
  ##maintainer='',
  ##maintainer_email='',

  # distribute-specific keys:
  ##include_package_data=True,
  ##exclude_package_data={},
  zip_safe=False,
  install_requires=requires_to_install_requires(REQUIRES),
  entry_points={
    'console_scripts': [
      'mkbootstrap=everyapp.bootstrap.mkbootstrap:main',
    ],
    ##'gui_scripts': [],
    ##'setuptools.installation': [],
  },
  ##extras_require={},
  ##setup_requires=[],
  ##dependency_links=[],
  namespace_packages=['everyapp'],
  ##test_suite='',
  ##tests_require=[],
  ##test_loader='',
  ##eager_resources=[],
  ##use_2to3=False,
  ##convert_2to3_doctests=False,
  ##use_2to3_fixers=[],
)
