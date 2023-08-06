#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.canonical__test ----------------------------------------===
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

# Python standard library, unit-testing
import unittest2

# Python patterns, scenario unit-testing
from python_patterns.unittest.scenario import ScenarioMeta

# Haiku language, built-in primitives
from haiku.builtin import builtinEnvironment
# Haiku language, environment mapping
from haiku.environment import Environment
# Haiku language, interpreter
from haiku.interpreter import BaseInterpreter
# Haiku language, s-expression pickler
from haiku.pickle import CanonicalExpressionPickler

# Haiku language, scenario testing
from haiku.utils.testing import (
  EvaluateScenarioTest, PicklerDumpScenarioTest, PicklerLoadScenarioTest)

SCENARIOS_b64encode = [
  dict(lisp   = '[9:b64encode\'3:\xff\x00\x00]',
       python = [{0:'b64encode',1:{0:'quote',1:'\xff\x00\x00'}}],
       eval_  = ['_wAA']),
  dict(lisp   = '[9:b64encode\'3:\x00\xff\x00]',
       python = [{0:'b64encode',1:{0:'quote',1:'\x00\xff\x00'}}],
       eval_  = ['AP8A']),
  dict(lisp   = '[9:b64encode\'3:\x00\x00\xff]',
       python = [{0:'b64encode',1:{0:'quote',1:'\x00\x00\xff'}}],
       eval_  = ['AAD_']),

  dict(lisp   = '[9:b64encode\':]',
       python = [{0:'b64encode',1:{0:'quote',1:''}}],
       eval_  = ['']),
  dict(lisp   = '[9:b64encode\'1:f]',
       python = [{0:'b64encode',1:{0:'quote',1:'f'}}],
       eval_  = ['Zg==']),
  dict(lisp   = '[9:b64encode\'2:fo]',
       python = [{0:'b64encode',1:{0:'quote',1:'fo'}}],
       eval_  = ['Zm8=']),
  dict(lisp   = '[9:b64encode\'3:foo]',
       python = [{0:'b64encode',1:{0:'quote',1:'foo'}}],
       eval_  = ['Zm9v']),
  dict(lisp   = '[9:b64encode\'4:foob]',
       python = [{0:'b64encode',1:{0:'quote',1:'foob'}}],
       eval_  = ['Zm9vYg==']),
  dict(lisp   = '[9:b64encode\'5:fooba]',
       python = [{0:'b64encode',1:{0:'quote',1:'fooba'}}],
       eval_  = ['Zm9vYmE=']),
  dict(lisp   = '[9:b64encode\'6:foobar]',
       python = [{0:'b64encode',1:{0:'quote',1:'foobar'}}],
       eval_  = ['Zm9vYmFy']),
]

class TestB64EncodeBuiltin(unittest2.TestCase):
  __metaclass__ = ScenarioMeta
  _pickler = CanonicalExpressionPickler()
  _environment = Environment(parent=builtinEnvironment)
  _interpreter = BaseInterpreter(pickler=_pickler, environment=_environment)
  class test_dump(PicklerDumpScenarioTest):
    scenarios = SCENARIOS_b64encode
  class test_load(PicklerLoadScenarioTest):
    scenarios = SCENARIOS_b64encode
  class test_eval(EvaluateScenarioTest):
    scenarios = SCENARIOS_b64encode

SCENARIOS_b64decode = [
dict(lisp   = '[9:b64decode\'4:_wAA]',
     python = [{0:'b64decode',1:{0:'quote',1:'_wAA'}}],
     eval_  = ['\xff\x00\x00']),
dict(lisp   = '[9:b64decode\'4:AP8A]',
     python = [{0:'b64decode',1:{0:'quote',1:'AP8A'}}],
     eval_  = ['\x00\xff\x00']),
dict(lisp   = '[9:b64decode\'4:AAD_]',
     python = [{0:'b64decode',1:{0:'quote',1:'AAD_'}}],
     eval_  = ['\x00\x00\xff']),

  dict(lisp   = '[9:b64decode\':]',
       python = [{0:'b64decode',1:{0:'quote',1:''}}],
       eval_  = ['']),
  dict(lisp   = '[9:b64decode\'4:Zg==]',
       python = [{0:'b64decode',1:{0:'quote',1:'Zg=='}}],
       eval_  = ['f']),
  dict(lisp   = '[9:b64decode\'4:Zm8=]',
       python = [{0:'b64decode',1:{0:'quote',1:'Zm8='}}],
       eval_  = ['fo']),
  dict(lisp   = '[9:b64decode\'4:Zm9v]',
       python = [{0:'b64decode',1:{0:'quote',1:'Zm9v'}}],
       eval_  = ['foo']),
  dict(lisp   = '[9:b64decode\'8:Zm9vYg==]',
       python = [{0:'b64decode',1:{0:'quote',1:'Zm9vYg=='}}],
       eval_  = ['foob']),
  dict(lisp   = '[9:b64decode\'8:Zm9vYmE=]',
       python = [{0:'b64decode',1:{0:'quote',1:'Zm9vYmE='}}],
       eval_  = ['fooba']),
  dict(lisp   = '[9:b64decode\'8:Zm9vYmFy]',
       python = [{0:'b64decode',1:{0:'quote',1:'Zm9vYmFy'}}],
       eval_  = ['foobar']),
]

class TestB64DecodeBuiltin(unittest2.TestCase):
  __metaclass__ = ScenarioMeta
  _pickler = CanonicalExpressionPickler()
  _environment = Environment(parent=builtinEnvironment)
  _interpreter = BaseInterpreter(pickler=_pickler, environment=_environment)
  class test_dump(PicklerDumpScenarioTest):
    scenarios = SCENARIOS_b64decode
  class test_load(PicklerLoadScenarioTest):
    scenarios = SCENARIOS_b64decode
  class test_eval(EvaluateScenarioTest):
    scenarios = SCENARIOS_b64decode

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
