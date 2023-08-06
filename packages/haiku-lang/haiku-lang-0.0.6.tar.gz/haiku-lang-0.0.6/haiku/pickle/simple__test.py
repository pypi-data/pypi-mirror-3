#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.simple__test -------------------------------------------===
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
from python_patterns.unittest.scenario import ScenarioMeta, ScenarioTest

# Python standard library, string input/output
from StringIO import StringIO

# Haiku language, built-in primitives
from haiku.builtin import builtinEnvironment
# Haiku language, environment mapping
from haiku.environment import Environment
# Haiku language, interpreter
from haiku.interpreter import BaseInterpreter
# Haiku language, s-expression pickler
from haiku.pickle import SimpleExpressionPickler
# Haiku language, type hierarchy
from haiku.types import *

# Haiku language, scenario testing
from haiku.utils.testing import (
  EvaluateScenarioTest, PicklerDumpScenarioTest, PicklerLoadScenarioTest)

SCENARIOS = [
  # Empty string (edge case):
  dict(lisp=u'',        python=[], eval_=[]),
  dict(lisp=u' ',       python=[], eval_=[], skip=['dump']),
  dict(lisp=u'\n',      python=[], eval_=[], skip=['dump']),
  dict(lisp=u'; test',  python=[], eval_=[], skip=['dump']),
  dict(lisp=u'; eos\n', python=[], eval_=[], skip=['dump']),

  # Symbol literals:
  dict(lisp=u'abc',     python=['abc'],           skip=['eval']),
  dict(lisp=u'a-b-c?',  python=['a-b-c?'],        skip=['eval']),
  dict(lisp=u'a b c ?', python=['a','b','c','?'], skip=['eval']),
  dict(lisp=u'#empty',  python=[''],              skip=['eval']),
  dict(lisp   = u'[b64decode \'IA==]',
       python = [' '],
       skip   = ['eval','load']),
  dict(lisp   = u'[b64decode \'AA==]',
       python = ['\0'],
       skip   = ['eval','load']),
  dict(lisp   = u'[b64decode \'AQIDBA==]',
       python = ['\x01\x02\x03\x04'],
       skip   = ['eval','load']),

  # Constant literals:
  dict(lisp=u'#nil',          python=[None], eval_=[None]),
  dict(lisp=u'# nil',         python=[None], eval_=[None], skip=['dump']),
  dict(lisp=u'#\nnil',        python=[None], eval_=[None], skip=['dump']),
  dict(lisp=u'#\n;test\nnil', python=[None], eval_=[None], skip=['dump']),

  dict(lisp=u'#f',          python=[False], eval_=[False]),
  dict(lisp=u'# f',         python=[False], eval_=[False], skip=['dump']),
  dict(lisp=u'#\nf',        python=[False], eval_=[False], skip=['dump']),
  dict(lisp=u'#\n;test\nf', python=[False], eval_=[False], skip=['dump']),

  dict(lisp=u'#t',          python=[True], eval_=[True]),
  dict(lisp=u'# t',         python=[True], eval_=[True], skip=['dump']),
  dict(lisp=u'#\nt',        python=[True], eval_=[True], skip=['dump']),
  dict(lisp=u'#\n;test\nt', python=[True], eval_=[True], skip=['dump']),

  # Integer literals:
  dict(lisp=u'0',   python=[0],     eval_=[0]),
  dict(lisp=u'30',  python=[30],    eval_=[30]),
  dict(lisp=u'03',  python=[3],     eval_=[3],  skip=['dump']),
  dict(lisp=u'+3',  python=[3],     eval_=[3],  skip=['dump']),
  dict(lisp=u'+ 3', python=['+',3],             skip=['eval']),
  dict(lisp=u'+-3', python=['+-3'],             skip=['eval']),
  dict(lisp=u'-+3', python=['-+3'],             skip=['eval']),
  dict(lisp=u'3',   python=[3],     eval_=[3]),
  dict(lisp=u'3L',  python=[3,'L'],             skip=['eval','dump']),
  dict(lisp=u'3f',  python=[3,'f'],             skip=['eval','dump']),
  dict(lisp   = u'36893488147419103232',
       python = [2**65],
       eval_  = [36893488147419103232L]),
  dict(lisp   = u'-36893488147419103232',
       python = [-2**65],
       eval_  = [-36893488147419103232L]),

  # Rational literals:
  dict(lisp=u'1/2',    python=[Fraction(1,2)],    eval_=[Fraction(1,2)]),
  dict(lisp=u'2/2',    python=[Fraction(1,1)],    eval_=[Fraction(1,1)],    skip=['dump']),
  dict(lisp=u'3/3000', python=[Fraction(1,1000)], eval_=[Fraction(1,1000)], skip=['dump']),
  dict(lisp=u'200/5',  python=[Fraction(40,1)],   eval_=[Fraction(40,1)],   skip=['dump']),
  dict(lisp=u'2/4',    python=[Fraction(1,2)],    eval_=[Fraction(1,2)],    skip=['dump']),
  dict(lisp=u'1 / 2',  python=[1, '/', 2],                                  skip=['eval']),
  dict(lisp=u'1/ 2',   python=[1, '/', 2],                                  skip=['eval','dump']),
  dict(lisp=u'1 /2',   python=[1, '/2'],                                    skip=['eval','dump']),
  dict(lisp=u'1/+2',   python=[1, '/+2'],                                   skip=['eval','dump']),
  dict(lisp=u'1/-2',   python=[1, '/-2'],                                   skip=['eval','dump']),
  dict(lisp=u'+1/2',   python=[Fraction(1,2)],    eval_=[Fraction(1,2)],    skip=['dump']),
  dict(lisp=u'-1/2',   python=[Fraction(-1,2)],   eval_=[Fraction(-1,2)]),

  # Unicode strings:
  dict(lisp=u'""',             python=[u""],  eval_=[u""]),
  dict(lisp=u'"-"',            python=[u"-"], eval_=[u"-"]),
  dict(lisp=u'"\\\\"',         python=[u"\u005c"],       eval_=[u"\u005c"]),
  dict(lisp=u'"\\\""',         python=[u"\u0022"],       eval_=[u"\u0022"]),
  dict(lisp=u'"\\\\\\\""',     python=[u"\u005c\u0022"], eval_=[u"\u005c\u0022"]),
  dict(lisp=u'"abc"',          python=[u"abc"],          eval_=[u"abc"]),
  dict(lisp=u'"123"',          python=[u"123"],          eval_=[u"123"]),
  dict(lisp=u'"#t = ; test"',  python=[u"#t = ; test"],  eval_=[u"#t = ; test"]),
  dict(lisp=u'"tsch\\xfcss!"', python=[u"tschüss!"],     eval_=[u"tschüss!"]),
  dict(lisp   = u'"\\u3053\\u3093\\u306b\\u3061\\u306f\\u4e16\\u754c\\uff01"',
       python = [u"こんにちは世界！"],
       eval_  = [u"こんにちは世界！"]),
  dict(lisp   = u"'-'[]",
       python = [
         Tuple([
           (0, 'quote'),
           (1, '-'),
         ]),
         Tuple([
           (0, 'quote'),
           (1, Tuple()),
         ]),
       ],
       eval_  = ['-', Tuple()],
       skip   =['dump']),
  dict(lisp   = u"'- '[]",
       python = [{0:'quote',1:'-'},{0:'quote',1:{}}],
       eval_  = ['-',{}]),
  # FIXME: add tests for smart quotes

  # Empty sequences (edge cases):
  dict(lisp=u'[]', python=[Tuple()],                                              skip=['eval']),
  dict(lisp=u'{}', python=[Tuple([(0, 'quote'), (1, Tuple())])], eval_=[Tuple()], skip=['dump']),
  dict(lisp=u'()', python=[Sequence()],                          eval_=[Sequence()]),
  # FIXME: implement correct pattern matching detection of eval-data tuples,
  #   and implement associated unit tests

  # Basic tuple forms:
  dict(lisp=u'[]',              python=[Tuple()],                             skip=['eval']),
  dict(lisp=u'[a]',             python=[{0:'a'}],                             skip=['eval']),
  dict(lisp=u'[a b c]',         python=[{0:'a',1:'b',2:'c'}],                 skip=['eval']),
  dict(lisp=u'[1 -2 3]',        python=[{0:1,1:-2,2:3}],                      skip=['eval']),
  dict(lisp=u'[a [b 1] [c 2]]', python=[{0:'a',1:{0:'b',1:1},2:{0:'c',1:2}}], skip=['eval']),

  # Complex tuple forms:
  dict(lisp   = u'[1 2 3 #nil:false true:#t]',
       python = [{0:1,1:2,2:3,'true':True,None:'false'}],
       skip   = ['eval']),
  dict(lisp   = u'[if [= 1 2] then:#nil else:"whew"]',
       python = [{0:'if',1:{0:'=',1:1,2:2},'then':None,'else':u"whew"}],
       eval_  = [u"whew"],
       skip   = ['dump', 'eval']),
  dict(lisp   = u'[if [= 1 2] else:"whew" then:#nil]',
       python = [{0:'if',1:{0:'=',1:1,2:2},'then':None,'else':u"whew"}],
       eval_  = [u"whew"],
       skip   = ['eval']),

  # Arithmetic operators:
  dict(lisp=u'[+ 0 1]',  python=[{0:'+',1:0L,2:1L}],  eval_=[1]),
  dict(lisp=u'[+ 2 3]',  python=[{0:'+',1:2L,2:3L}],  eval_=[5]),
  dict(lisp=u'[+ 5 6]',  python=[{0:'+',1:5L,2:6L}],  eval_=[11]),
  dict(lisp=u'[+ -1 1]', python=[{0:'+',1:-1L,2:1L}], eval_=[0]),

  dict(lisp=u'[- 0 1]',  python=[{0:'-',1:0L,2:1L}],  eval_=[-1]),
  dict(lisp=u'[- 2 3]',  python=[{0:'-',1:2L,2:3L}],  eval_=[-1]),
  dict(lisp=u'[- 9 2]',  python=[{0:'-',1:9L,2:2L}],  eval_=[7]),
  dict(lisp=u'[- 1 -1]', python=[{0:'-',1:1L,2:-1L}], eval_=[2]),

  dict(lisp=u'[/ 0 1]',  python=[{0:'/',1:0L,2:1L}],  eval_=[0]),
  dict(lisp=u'[/ 2 3]',  python=[{0:'/',1:2L,2:3L}],  eval_=[Fraction(2,3)]),
  dict(lisp=u'[/ 5 6]',  python=[{0:'/',1:5L,2:6L}],  eval_=[Fraction(5,6)]),
  dict(lisp=u'[/ -5 4]', python=[{0:'/',1:-5L,2:4L}], eval_=[-Fraction(5,4)]),
  dict(lisp=u'[/ -4 4]', python=[{0:'/',1:-4L,2:4L}], eval_=[-1]),
  dict(lisp=u'[/ -3 4]', python=[{0:'/',1:-3L,2:4L}], eval_=[-Fraction(3,4)]),
  dict(lisp=u'[/ -2 4]', python=[{0:'/',1:-2L,2:4L}], eval_=[-Fraction(1,2)]),
  dict(lisp=u'[/ -1 4]', python=[{0:'/',1:-1L,2:4L}], eval_=[-Fraction(1,4)]),
  dict(lisp=u'[/ 0 4]',  python=[{0:'/',1:0L,2:4L}],  eval_=[0]),
  dict(lisp=u'[/ 1 4]',  python=[{0:'/',1:1L,2:4L}],  eval_=[Fraction(1,4)]),
  dict(lisp=u'[/ 2 4]',  python=[{0:'/',1:2L,2:4L}],  eval_=[Fraction(1,2)]),
  dict(lisp=u'[/ 3 4]',  python=[{0:'/',1:3L,2:4L}],  eval_=[Fraction(3,4)]),
  dict(lisp=u'[/ 4 4]',  python=[{0:'/',1:4L,2:4L}],  eval_=[1]),
  dict(lisp=u'[/ 5 4]',  python=[{0:'/',1:5L,2:4L}],  eval_=[Fraction(5,4)]),

  dict(lisp=u'[* 0 1]', python=[{0:'*',1:0L,2:1L}], eval_=[0]),
  dict(lisp=u'[* 2 3]', python=[{0:'*',1:2L,2:3L}], eval_=[6]),
  dict(lisp=u'[* 5 6]', python=[{0:'*',1:5L,2:6L}], eval_=[30]),
  dict(lisp   = u'[* [* 9 12] 30]',
       python = [{0:'*',1:{0:'*',1:9L,2:12L},2:30L}],
       eval_  = [3240]),

  dict(lisp=u'[divmod 0 1]',  python=[{0:'divmod',1:0L,2:1L}],  eval_=[{'quotient':0, 'remainder':0}]),
  dict(lisp=u'[divmod 3 2]',  python=[{0:'divmod',1:3L,2:2L}],  eval_=[{'quotient':1, 'remainder':1}]),
  dict(lisp=u'[divmod 29 7]', python=[{0:'divmod',1:29L,2:7L}], eval_=[{'quotient':4, 'remainder':1}]),

  dict(lisp=u'[pow 0 8]',    python=[{0:'pow',1:0L,2:8L}],       eval_=[0]),
  dict(lisp=u'[pow 1 4]',    python=[{0:'pow',1:1L,2:4L}],       eval_=[1]),
  dict(lisp=u'[pow 2 3]',    python=[{0:'pow',1:2L,2:3L}],       eval_=[8]),
  dict(lisp=u'[pow 3 3]',    python=[{0:'pow',1:3L,2:3L}],       eval_=[27]),
  dict(lisp=u'[pow 7 2 29]', python=[{0:'pow',1:7L,2:2L,3:29L}], eval_=[20]),
  dict(lisp=u'[pow -1 0]',   python=[{0:'pow',1:-1L,2:0L}],      eval_=[1]),
  dict(lisp=u'[pow -1 1]',   python=[{0:'pow',1:-1L,2:1L}],      eval_=[-1]),
  dict(lisp=u'[pow -1 2]',   python=[{0:'pow',1:-1L,2:2L}],      eval_=[1]),
  dict(lisp=u'[pow -1 3]',   python=[{0:'pow',1:-1L,2:3L}],      eval_=[-1]),
  dict(lisp=u'[pow -1 4]',   python=[{0:'pow',1:-1L,2:4L}],      eval_=[1]),

  # Logical operators:
  # FIXME: add tests for [any ...]
  # FIXME: add tests for [all ...]
  dict(lisp=u'[& #f #f]', python=[{0:'&',1:False,2:False}], eval_=[False]),
  dict(lisp=u'[& #f #t]', python=[{0:'&',1:False,2: True}], eval_=[False]),
  dict(lisp=u'[& #t #f]', python=[{0:'&',1: True,2:False}], eval_=[False]),
  dict(lisp=u'[& #t #t]', python=[{0:'&',1: True,2: True}], eval_=[True]),
  dict(lisp=u'[| #f #f]', python=[{0:'|',1:False,2:False}], eval_=[False]),
  dict(lisp=u'[| #f #t]', python=[{0:'|',1:False,2: True}], eval_=[True]),
  dict(lisp=u'[| #t #f]', python=[{0:'|',1: True,2:False}], eval_=[True]),
  dict(lisp=u'[| #t #t]', python=[{0:'|',1: True,2: True}], eval_=[True]),
  dict(lisp=u'[^ #f #f]', python=[{0:'^',1:False,2:False}], eval_=[False]),
  dict(lisp=u'[^ #f #t]', python=[{0:'^',1:False,2: True}], eval_=[True]),
  dict(lisp=u'[^ #t #f]', python=[{0:'^',1: True,2:False}], eval_=[True]),
  dict(lisp=u'[^ #t #t]', python=[{0:'^',1: True,2: True}], eval_=[False]),
  dict(lisp=u'[! #f]',    python=[{0:'!',1:False}],         eval_=[True]),
  dict(lisp=u'[! #t]',    python=[{0:'!',1: True}],         eval_=[False]),
  dict(lisp=u'[~ #f]',    python=[{0:'~',1:False}],         eval_=[-1]),
  dict(lisp=u'[~ #t]',    python=[{0:'~',1: True}],         eval_=[-2]),

  # Comparative operators:
  dict(lisp=u'[< -1 -1]',  python=[{0: '<',1:-1L,2:-1L}], eval_=[False]),
  dict(lisp=u'[< -1 1]',   python=[{0: '<',1:-1L,2:1L}],  eval_=[True]),
  dict(lisp=u'[< 1 -1]',   python=[{0: '<',1:1L,2:-1L}],  eval_=[False]),
  dict(lisp=u'[< 1 1]',    python=[{0: '<',1:1L,2:1L}],   eval_=[False]),
  dict(lisp=u'[<= -1 -1]', python=[{0:'<=',1:-1L,2:-1L}], eval_=[True]),
  dict(lisp=u'[<= -1 1]',  python=[{0:'<=',1:-1L,2:1L}],  eval_=[True]),
  dict(lisp=u'[<= 1 -1]',  python=[{0:'<=',1:1L,2:-1L}],  eval_=[False]),
  dict(lisp=u'[<= 1 1]',   python=[{0:'<=',1:1L,2:1L}],   eval_=[True]),
  dict(lisp=u'[= -1 -1]',  python=[{0: '=',1:-1L,2:-1L}], eval_=[True]),
  dict(lisp=u'[= -1 1]',   python=[{0: '=',1:-1L,2:1L}],  eval_=[False]),
  dict(lisp=u'[= 1 -1]',   python=[{0: '=',1:1L,2:-1L}],  eval_=[False]),
  dict(lisp=u'[= 1 1]',    python=[{0: '=',1:1L,2:1L}],   eval_=[True]),
  dict(lisp=u'[>= -1 -1]', python=[{0:'>=',1:-1L,2:-1L}], eval_=[True]),
  dict(lisp=u'[>= -1 1]',  python=[{0:'>=',1:-1L,2:1L}],  eval_=[False]),
  dict(lisp=u'[>= 1 -1]',  python=[{0:'>=',1:1L,2:-1L}],  eval_=[True]),
  dict(lisp=u'[>= 1 1]',   python=[{0:'>=',1:1L,2:1L}],   eval_=[True]),
  dict(lisp=u'[> -1 -1]',  python=[{0: '>',1:-1L,2:-1L}], eval_=[False]),
  dict(lisp=u'[> -1 1]',   python=[{0: '>',1:-1L,2:1L}],  eval_=[False]),
  dict(lisp=u'[> 1 -1]',   python=[{0: '>',1:1L,2:-1L}],  eval_=[True]),
  dict(lisp=u'[> 1 1]',    python=[{0: '>',1:1L,2:1L}],   eval_=[False]),
  dict(lisp=u'[!= -1 -1]', python=[{0:'!=',1:-1L,2:-1L}], eval_=[False]),
  dict(lisp=u'[!= -1 1]',  python=[{0:'!=',1:-1L,2:1L}],  eval_=[True]),
  dict(lisp=u'[!= 1 -1]',  python=[{0:'!=',1:1L,2:-1L}],  eval_=[True]),
  dict(lisp=u'[!= 1 1]',   python=[{0:'!=',1:1L,2:1L}],   eval_=[False]),

  # String operators:
  dict(lisp   = u'[cat "Hello, " "world!"]',
       python = [{0:'cat', 1:u"Hello, ", 2:u"world!"}],
       eval_  = [u"Hello, world!"]),
]

from haiku.builtin import builtinEnvironment
from haiku.environment import Environment
from haiku.interpreter import BaseInterpreter
class TestSimpleExpressionPickler(unittest2.TestCase):
  """Test serialization and deserialization of Lisp code to/from Python
  objects using the `SimpleExpressionPickler` class."""
  __metaclass__ = ScenarioMeta
  _pickler = SimpleExpressionPickler()
  _environment = Environment(parent=builtinEnvironment)
  _interpreter = BaseInterpreter(_pickler, environment=_environment)
  class test_dump(PicklerDumpScenarioTest):
    scenarios = SCENARIOS
  class test_load(PicklerLoadScenarioTest):
    scenarios = SCENARIOS
  class test_eval_load(EvaluateScenarioTest):
    scenarios = SCENARIOS

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
