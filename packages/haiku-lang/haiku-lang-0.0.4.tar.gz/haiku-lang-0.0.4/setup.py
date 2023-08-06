#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === setup.py ------------------------------------------------------------===
# Copyright © 2011-2012, RokuSigma Inc. and contributors. See AUTHORS for more
# details.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well as
# documentation, with or without modification, are permitted provided that the
# following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * The names of the copyright holders or contributors may not be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND
# DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ===----------------------------------------------------------------------===

import os

from distutils.core import setup

VERSION = (0,0,4, 'final', 0)

def get_version():
  version = '%s.%s' % (VERSION[0], VERSION[1])
  if VERSION[2]:
    version = '%s.%s' % (version, VERSION[2])
  if VERSION[3:] == ('alpha', 0):
    version = '%s pre-alpha' % version
  else:
    if VERSION[3] != 'final':
      version = '%s %s' % (version, VERSION[3])
      if VERSION[4] != 0:
        version = '%s%s' % (version, VERSION[4])
  return version

# Compile the list of packages available, because distutils doesn't have an
# easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
  os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('haiku'):
  # Ignore dirnames that start with '.'
  for i, dirname in enumerate(dirnames):
    if dirname.startswith('.'): del dirnames[i]
  if '__init__.py' in filenames:
    pkg = dirpath.replace(os.path.sep, '.')
    if os.path.altsep:
      pkg = pkg.replace(os.path.altsep, '.')
    packages.append(pkg)
  elif filenames:
    prefix = dirpath[6:] # Strip "haiku/" or "haiku\"
    for f in filenames:
      data_files.append(os.path.join(prefix, f))

version = get_version().replace(' ', '-')
setup(name='haiku-lang',
  version=version,
  description='An embedable LISP implemented on top of the Python interpreter.',
  install_requires=[
    'LEPL>=5.1.1',
    'bitstring>=3.0.2',
    'python-patterns>=0.0.1',
  ],
  author='RokuSigma Inc.',
  author_email='haiku-lang@monetize.io',
  url='http://www.github.com/monetizeio/haiku-lang/',
  download_url='http://pypi.python.org/packages/source/h/haiku-lang/haiku-lang-%s.tar.gz' % version,
  package_dir={'haiku': 'haiku'},
  packages=packages,
  package_data={'haiku': data_files},
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'License :: Other/Proprietary License',
    'Operating System :: OS Independent',
    'Programming Language :: Lisp',
    'Programming Language :: Python',
    'Topic :: Software Development :: Interpreters',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
  ],
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
