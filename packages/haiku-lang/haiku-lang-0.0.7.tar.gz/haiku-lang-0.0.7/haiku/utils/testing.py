#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.utils.testing -------------------------------------------------===
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

# Python standard library, string input/output
from StringIO import StringIO

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioTest

__all__ = [
  'EvaluateScenarioTest',
  'PicklerDumpScenarioTest',
  'PicklerLoadScenarioTest',
]

class PicklerDumpScenarioTest(ScenarioTest):
  """Test serialization of Lisp code from Python objects by means of a pickler
  object."""
  def __test__(self, **kwargs):
    # Check if it is okay to run this scenario:
    skip = kwargs.get('skip', [])
    if 'dump' in skip:
      self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
    # Extract scenario parameters:
    #
    # Yes, I realize that dict.get() allows a default to be specified, but
    # that would require that self._attribute aloways be defined, which need
    # not be the case if the attribute is specified for every scenario.
    if 'lisp'    in kwargs: lisp    = kwargs.get('lisp')
    else:                   lisp    = self._lisp
    if 'python'  in kwargs: python  = kwargs.get('python')
    else:                   python  = self._python
    if 'pickler' in kwargs: pickler = kwargs.get('pickler')
    else:                   pickler = self._pickler
    # Compare dump(StringIO) vs the prepared Lisp:
    if isinstance(lisp, unicode):
      ostream = StringIO()
      pickler.dump(ostream, *python) # utf-8 is dump()'s default encoding
      self.assertEqual(lisp, ostream.getvalue().decode('utf-8'))
      ostream = StringIO()
      pickler.dump(ostream, *python, encoding='utf-16')
      self.assertEqual(lisp, ostream.getvalue().decode('utf-16'))
    else:
      ostream = StringIO()
      pickler.dump(ostream, *python)
      self.assertEqual(lisp, ostream.getvalue())
    # Compare dumps() vs the prepared Lisp:
    self.assertEqual(lisp, pickler.dumps(*python))

class PicklerLoadScenarioTest(ScenarioTest):
  """Test deserialization of Lisp code to Python objects by means of a pickler
  object."""
  def __test__(self, **kwargs):
    # Check if it is okay to run this scenario:
    skip = kwargs.pop('skip', [])
    if 'load' in skip:
      self.skipTest(u"Scenario not compatible with pickle.dump(); skipping...")
    # Extract scenario parameters:
    if 'lisp'    in kwargs: lisp    = kwargs.get('lisp')
    else:                   lisp    = self._lisp
    if 'python'  in kwargs: python  = kwargs.get('python')
    else:                   python  = self._python
    if 'pickler' in kwargs: pickler = kwargs.get('pickler')
    else:                   pickler = self._pickler
    # Compare load(StringIO) vs the prepared Python:
    if isinstance(lisp, unicode):
      istream = StringIO(lisp.encode('utf-8')) # utf-8 is load()'s default
      self.assertEqual(pickler.load(istream), python)
      istream = StringIO(lisp.encode('utf-16'))
      self.assertEqual(pickler.load(istream, encoding='utf-16'), python)
    else:
      istream = StringIO(lisp)
      self.assertEqual(pickler.load(istream), python)
    # Compare loads() vs the prepared Python:
    self.assertEqual(pickler.loads(lisp), python)

class EvaluateScenarioTest(ScenarioTest):
  "Test evaluation of Lisp code by means of an interpreter object."
  def __test__(self, **kwargs):
    # Check if it is okay to run this scenario:
    skip = kwargs.pop('skip', [])
    skip_eval        =              'eval'        in skip
    skip_eval_lisp   = skip_eval or 'eval-lisp'   in skip
    skip_eval_python = skip_eval or 'eval-python' in skip
    if skip_eval or (skip_eval_lisp and skip_eval_python):
      self.skipTest(u"Scenario not compatible with interpreter.evaluate(); skipping...")
    # Extract scenario parameters:
    if 'eval_'       in kwargs: eval_       = kwargs.get('eval_')
    else:                       eval_       = self._eval_
    if 'pickler'     in kwargs: pickler     = kwargs.get('pickler')
    else:                       pickler     = self._pickler
    if 'interpreter' in kwargs: interpreter = kwargs.get('interpreter')
    else:                       interpreter = self._interpreter
    # Perform evaluation and compare:
    if not skip_eval_lisp:
      if 'lisp'      in kwargs: lisp        = kwargs.get('lisp')
      else:                     lisp        = self._lisp
      # Compare interpreter.evaluate(loads(lisp)) vs hand-computed value:
      self.assertEqual(eval_, interpreter.evaluate(pickler.loads(lisp)))
    if not skip_eval_python:
      if 'python'    in kwargs: python      = kwargs.get('python')
      else:                     python      = self._python
      # Compare interpreter.evaluate(python) vs hand-computed value:
      self.assertEqual(eval_, interpreter.evaluate(python))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
