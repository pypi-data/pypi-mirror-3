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
# Haiku language, type hierarchy
from haiku.types import *

# Haiku language, scenario testing
from haiku.utils.testing import (
  EvaluateScenarioTest, PicklerDumpScenarioTest, PicklerLoadScenarioTest)

SCENARIOS = [
  # Empty string (edge case):
  dict(lisp='', python=[], eval_=[]),

  # Symbol literals:
  dict(lisp='3:abc',        python=['abc'],           skip=['eval']),
  dict(lisp='6:a-b-c?',     python=['a-b-c?'],        skip=['eval']),
  dict(lisp='1:a1:b1:c1:?', python=['a','b','c','?'], skip=['eval']),
  dict(lisp=':',            python=[''],              skip=['eval']),
  dict(lisp='1: ',          python=[' '],             skip=['eval']),
  dict(lisp='1:\0',         python=['\x00'],          skip=['eval']),
  dict(lisp   = '4:\001\002\003\004',
       python = ['\x01\x02\x03\x04'],
       skip   = ['eval']),

  # Constant literals:
  dict(lisp='[3:nil]',   python=[None],  eval_=[None],  skip=['load']),
  dict(lisp='[5:false]', python=[False], eval_=[False], skip=['load']),
  dict(lisp='[4:true]',  python=[True],  eval_=[True],  skip=['load']),

  # Integer literals:
  dict(lisp='[7:integer\'1:\xfe]',     python=[-2],   eval_=[-2],   skip=['load']),
  dict(lisp='[7:integer\'1:\xff]',     python=[-1],   eval_=[-1],   skip=['load']),
  dict(lisp='[7:integer\':]',          python=[0],    eval_=[0],    skip=['load']),
  dict(lisp='[7:integer\'1:\x01]',     python=[1],    eval_=[1],    skip=['load']),
  dict(lisp='[7:integer\'1:\x02]',     python=[2],    eval_=[2],    skip=['load']),
  dict(lisp='[7:integer\'1:\x1e]',     python=[30],   eval_=[30],   skip=['load']),
  dict(lisp='[7:integer\'1: ]',        python=[32],   eval_=[32],   skip=['load']),
  dict(lisp='[7:integer\'1:\x7f]',     python=[127],  eval_=[127],  skip=['load']),
  dict(lisp='[7:integer\'2:\x80\x00]', python=[128],  eval_=[128],  skip=['load']),
  dict(lisp='[7:integer\'1:\x81]',     python=[-127], eval_=[-127], skip=['load']),
  dict(lisp='[7:integer\'1:\x80]',     python=[-128], eval_=[-128], skip=['load']),
  dict(lisp='[7:integer\'2:\x7f\xff]', python=[-129], eval_=[-129], skip=['load']),
  dict(lisp   = '[7:integer\'9:\x00\x00\x00\x00\x00\x00\x00\x00\x02]',
       python = [2**65],
       eval_  = [36893488147419103232L],
       skip   = ['load']),
  dict(lisp   = '[7:integer\'9:\x00\x00\x00\x00\x00\x00\x00\x00\xfe]',
       python = [-2**65],
       eval_  = [-36893488147419103232L],
       skip   = ['load']),

  # Rational literals:
  dict(lisp   = '[8:rational[7:integer\'1:\x01][7:integer\'1:\x02]]',
       python = [Fraction(1,2)],
       eval_  = [Fraction(1,2)],
       skip   = ['load']),
  dict(lisp   = '[8:rational[7:integer\'1:\x01][7:integer\'1:\x02]]',
       python = [Fraction(2,4)],
       skip   = ['eval','load']),
  dict(lisp   = '[8:rational[7:integer\'1:\xff][7:integer\'1:\x02]]',
       python = [Fraction(-1,2)],
       eval_  = [Fraction(-1,2)],
       skip   = ['load']),
  dict(lisp   = '[8:rational[7:integer\'1:\xff][7:integer\'1:\x02]]',
       python = [Fraction(1,-2)],
       skip   = ['eval','load']),
  dict(lisp   = '[8:rational[7:integer\'1:\x01][7:integer\'1:\x02]]',
       python = [Fraction(-1,-2)],
       skip   = ['eval','load']),
  dict(lisp   = '[8:rational[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [Fraction(1,1)],
       eval_  = [Fraction(1,1)],
       skip   = ['load']),
  dict(lisp   = '[8:rational[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [Fraction(2,2)],
       skip   = ['eval','load']),
  dict(lisp   = '[8:rational[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [Fraction(2,2)],
       skip   = ['eval','load']),
  dict(lisp   = '[8:rational[7:integer\'2:\x93\x2e][7:integer\'3:\xbc\x34\x02]]',
       python = [Fraction(11923,144572)],
       eval_  = [Fraction(11923,144572)],
       skip   = ['load']),

  # Unicode strings:
  dict(lisp   = '[6:decode\':=\'8:encoding\'5:utf-8]',
       python = [u""],
       eval_  = [u""],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'1::=\'8:encoding\'5:utf-8]',
       python = [u":"],
       eval_  = [u":"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'1:\\=\'8:encoding\'5:utf-8]',
       python = [u"\u005c"],
       eval_  = [u"\u005c"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'1:\"=\'8:encoding\'5:utf-8]',
       python = [u"\u0022"],
       eval_  = [u"\u0022"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'2:\\\"=\'8:encoding\'5:utf-8]',
       python = [u"\u005c\u0022"],
       eval_  = [u"\u005c\u0022"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'3:abc=\'8:encoding\'5:utf-8]',
       python = [u"abc"],
       eval_  = [u"abc"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'3:123=\'8:encoding\'5:utf-8]',
       python = [u"123"],
       eval_  = [u"123"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'1::=\'8:encoding\'5:utf-8]',
       python = [u":"],
       eval_  = [u":"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'14:[7:integer1: ]=\'8:encoding\'5:utf-8]',
       python = [u"[7:integer1: ]"],
       eval_  = [u"[7:integer1: ]"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'9:tsch\xc3\xbcss!=\'8:encoding\'5:utf-8]',
       python = [u"tschüss!"],
       eval_  = [u"tschüss!"],
       skip   = ['load']),
  dict(lisp   = '[6:decode\'24:\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81'
                '\xa1\xe3\x81\xaf\xe4\xb8\x96\xe7\x95\x8c\xef\xbc\x81=\'8:e'
                'ncoding\'5:utf-8]',
       python = [u"こんにちは世界！"],
       eval_  = [u"こんにちは世界！"],
       skip   = ['load']),

  # Empty sequences (edge cases):
  dict(lisp='[]', python=[{}],                           skip=['eval']),
  dict(lisp='{}', python=[{0:'quote',1:{}}], eval_=[{}]),
  dict(lisp='()', python=[()],               eval_=[()]),
  # FIXME: implement correct pattern matching detection of eval-data tuples,
  #   and implement associated unit tests

  # Basic tuple forms:
  dict(lisp   = '[:]',
       python = [{0:''}],
       skip   = ['eval']),
  dict(lisp   = '[1:a]',
       python = [{0:'a'}],
       skip   = ['eval']),
  dict(lisp   = '[1:a1:b1:c]',
       python = [{0:'a',1:'b',2:'c'}],
       skip   = ['eval']),
  dict(lisp   = '[[7:integer\'1:\x01][7:integer\'1:\xfe][7:integer\'1:\x03]]',
       python = [{0:1,1:-2,2:3}],
       skip   = ['eval','load']),
  dict(lisp   = '[1:a[1:b[7:integer\'1:\x01]][1:c[7:integer\'1:\x02]]]',
       python = [{0:'a',1:{0:'b',1:1},2:{0:'c',1:2}}],
       skip   = ['eval','load']),

  # Complex tuple forms:
  dict(lisp   = '[[7:integer\'1:\x01][7:integer\'1:\x02][7:integer\'1:\x03]='
                '\'4:true[4:true]=[3:nil]\'5:false]',
       python = [
         Tuple([
           (0, 1),
           (1, 2),
           (2, 3),
           (None, Tuple([
             (0, 'quote'),
             (1, 'false')])),
           (Tuple([
             (0, 'quote'),
             (1, 'true')]), True),
         ])],
       skip   = ['eval','load']),
  # FIXME: the next two tests are commented out because at this time they do
  #   not run deterministically as the ordering of tuples depends on their
  #   memory location. This needs to be fixed somehow, someway!
  #dict(lisp   = '[2:if[1:=[7:integer\'1:\x01][7:integer\'1:\x02]]=\'4:then[3:'
  #              'nil]=\'4:else[6:decode4:whew=\'8:encoding\'5:utf-8]]',
  #     python = [
  #       Tuple([
  #         (0, 'if'),
  #         (1, Tuple([
  #             (0, '='),
  #             (1, 1),
  #             (2, 2),
  #           ])),
  #         (Tuple([
  #             (0, 'quote'),
  #             (1, 'then'),
  #           ]), None),
  #         (Tuple([
  #             (0, 'quote'),
  #             (1, 'else'),
  #           ]), u"whew"),
  #       ])],
  #     eval_  = [u"whew"],
  #     skip   = ['dump','load']),
  #dict(lisp   = '[2:if[1:=[7:integer\'1:\x01][7:integer\'1:\x02]]=\'4:else[6:'
  #              'decode4:whew=\'8:encoding\'5:utf-8]]=\'4:then[3:nil]',
  #     python = [
  #       Tuple([
  #         (0, 'if'),
  #         (1, Tuple([
  #             (0, '='),
  #             (1, 1),
  #             (2, 2),
  #           ])),
  #         (Tuple([
  #             (0, 'quote'),
  #             (1, 'then'),
  #           ]), None),
  #         (Tuple([
  #             (0, 'quote'),
  #             (1, 'else'),
  #           ]), u"whew"),
  #       ])],
  #     eval_  = [u"whew"],
  #     skip   = ['load']),

  # Integer arithmetic operators:
  dict(lisp   = '[1:+[7:integer\':][7:integer\'1:\x01]]',
       python = [{0:'+',1:0L,2:1L}],
       eval_  = [1],
       skip   = ['load']),
  dict(lisp   = '[1:+[7:integer\'1:\x02][7:integer\'1:\x03]]',
       python = [{0:'+',1:2L,2:3L}],
       eval_  = [5],
       skip   = ['load']),
  dict(lisp   = '[1:+[7:integer\'1:\x05][7:integer\'1:\x06]]',
       python = [{0:'+',1:5L,2:6L}],
       eval_  = [11],
       skip   = ['load']),
  dict(lisp   = '[1:+[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0:'+',1:-1L,2:1L}],
       eval_  = [0],
       skip   = ['load']),

  dict(lisp   = '[1:-[7:integer\':][7:integer\'1:\x01]]',
       python = [{0:'-',1:0L,2:1L}],
       eval_  = [-1],
       skip   = ['load']),
  dict(lisp   = '[1:-[7:integer\'1:\x02][7:integer\'1:\x03]]',
       python = [{0:'-',1:2L,2:3L}],
       eval_  = [-1],
       skip   = ['load']),
  dict(lisp   = '[1:-[7:integer\'1:\x09][7:integer\'1:\x02]]',
       python = [{0:'-',1:9L,2:2L}],
       eval_  = [7],
       skip   = ['load']),
  dict(lisp   = '[1:-[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0:'-',1:1L,2:-1L}],
       eval_  = [2],
       skip   = ['load']),

  dict(lisp   = '[1:/[7:integer\':][7:integer\'1:\x01]]',
       python = [{0:'/',1:0L,2:1L}],
       eval_  = [0],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x02][7:integer\'1:\x03]]',
       python = [{0:'/',1:2L,2:3L}],
       eval_  = [Fraction(2,3)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x05][7:integer\'1:\x06]]',
       python = [{0:'/',1:5L,2:6L}],
       eval_  = [Fraction(5,6)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\xfb][7:integer\'1:\x04]]',
       python = [{0:'/',1:-5L,2:4L}],
       eval_  = [-Fraction(5,4)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\xfc][7:integer\'1:\x04]]',
       python = [{0:'/',1:-4L,2:4L}],
       eval_  = [-1],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\xfd][7:integer\'1:\x04]]',
       python = [{0:'/',1:-3L,2:4L}],
       eval_  = [-Fraction(3,4)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\xfe][7:integer\'1:\x04]]',
       python = [{0:'/',1:-2L,2:4L}],
       eval_  = [-Fraction(1,2)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\xff][7:integer\'1:\x04]]',
       python = [{0:'/',1:-1L,2:4L}],
       eval_  = [-Fraction(1,4)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\':][7:integer\'1:\x04]]',
       python = [{0:'/',1:0L,2:4L}],
       eval_  = [0],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x01][7:integer\'1:\x04]]',
       python = [{0:'/',1:1L,2:4L}],
       eval_  = [Fraction(1,4)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x02][7:integer\'1:\x04]]',
       python = [{0:'/',1:2L,2:4L}],
       eval_  = [Fraction(1,2)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x03][7:integer\'1:\x04]]',
       python = [{0:'/',1:3L,2:4L}],
       eval_  = [Fraction(3,4)],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x04][7:integer\'1:\x04]]',
       python = [{0:'/',1:4L,2:4L}],
       eval_  = [1],
       skip   = ['load']),
  dict(lisp   = '[1:/[7:integer\'1:\x05][7:integer\'1:\x04]]',
       python = [{0:'/',1:5L,2:4L}],
       eval_  = [Fraction(5,4)],
       skip   = ['load']),

  dict(lisp   = '[1:*[7:integer\':][7:integer\'1:\x01]]',
       python = [{0:'*',1:0L,2:1L}],
       eval_  = [0],
       skip   = ['load']),
  dict(lisp   = '[1:*[7:integer\'1:\x02][7:integer\'1:\x03]]',
       python = [{0:'*',1:2L,2:3L}],
       eval_  = [6],
       skip   = ['load']),
  dict(lisp   = '[1:*[7:integer\'1:\x05][7:integer\'1:\x06]]',
       python = [{0:'*',1:5L,2:6L}],
       eval_  = [30],
       skip   = ['load']),

  dict(lisp   = '[6:divmod[7:integer\':][7:integer\'1:\x01]]',
       python = [{0:'divmod',1:0L,2:1L}],
       eval_  = [{'quotient':0, 'remainder':0}],
       skip   = ['load']),
  dict(lisp   = '[6:divmod[7:integer\'1:\x03][7:integer\'1:\x02]]',
       python = [{0:'divmod',1:3L,2:2L}],
       eval_  = [{'quotient':1, 'remainder':1}],
       skip   = ['load']),
  dict(lisp   = '[6:divmod[7:integer\'1:\x1d][7:integer\'1:\x07]]',
       python = [{0:'divmod',1:29L,2:7L}],
       eval_  = [{'quotient':4, 'remainder':1}],
       skip   = ['load']),

  dict(lisp   = '[3:pow[7:integer\':][7:integer\'1:\x08]]',
       python = [{0:'pow',1:0L,2:8L}],
       eval_  = [0],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\x01][7:integer\'1:\x04]]',
       python = [{0:'pow',1:1L,2:4L}],
       eval_  = [1],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\x02][7:integer\'1:\x03]]',
       python = [{0:'pow',1:2L,2:3L}],
       eval_  = [8],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\x03][7:integer\'1:\x03]]',
       python = [{0:'pow',1:3L,2:3L}],
       eval_  = [27],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\x07][7:integer\'1:\x02][7:integer\'1:\x1d]]',
       python = [{0:'pow',1:7L,2:2L,3:29L}],
       eval_  = [20],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\xff][7:integer\':]]',
       python = [{0:'pow',1:-1L,2:0L}],
       eval_  = [1],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0:'pow',1:-1L,2:1L}],
       eval_  = [-1],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\xff][7:integer\'1:\x02]]',
       python = [{0:'pow',1:-1L,2:2L}],
       eval_  = [1],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\xff][7:integer\'1:\x03]]',
       python = [{0:'pow',1:-1L,2:3L}],
       eval_  = [-1],
       skip   = ['load']),
  dict(lisp   = '[3:pow[7:integer\'1:\xff][7:integer\'1:\x04]]',
       python = [{0:'pow',1:-1L,2:4L}],
       eval_  = [1],
       skip   = ['load']),

  # Logical operators:
  dict(lisp   = '[1:&[5:false][5:false]]',
       python = [{0:'&',1:False,2:False}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:&[5:false][4:true]]',
       python = [{0:'&',1:False,2: True}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:&[4:true][5:false]]',
       python = [{0:'&',1: True,2:False}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:&[4:true][4:true]]',
       python = [{0:'&',1: True,2: True}],
       eval_  = [True],
       skip   = ['load']),

  dict(lisp   = '[1:|[5:false][5:false]]',
       python = [{0:'|',1:False,2:False}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:|[5:false][4:true]]',
       python = [{0:'|',1:False,2: True}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:|[4:true][5:false]]',
       python = [{0:'|',1: True,2:False}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:|[4:true][4:true]]',
       python = [{0:'|',1: True,2: True}],
       eval_  = [True],
       skip   = ['load']),

  dict(lisp   = '[1:^[5:false][5:false]]',
       python = [{0:'^',1:False,2:False}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:^[5:false][4:true]]',
       python = [{0:'^',1:False,2: True}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:^[4:true][5:false]]',
       python = [{0:'^',1: True,2:False}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:^[4:true][4:true]]',
       python = [{0:'^',1: True,2: True}],
       eval_  = [False],
       skip   = ['load']),

  dict(lisp   = '[1:![5:false]]',
       python = [{0:'!',1:False}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:![4:true]]',
       python = [{0:'!',1: True}],
       eval_  = [False],
       skip   = ['load']),

  dict(lisp   = '[1:~[5:false]]',
       python = [{0:'~',1:False}],
       eval_  = [-1],
       skip   = ['load']),
  dict(lisp   = '[1:~[4:true]]',
       python = [{0:'~',1: True}],
       eval_  = [-2],
       skip   = ['load']),

  # Comparative operators:
  dict(lisp   = '[1:<[7:integer\'1:\xff][7:integer\'1:\xff]]',
       python = [{0: '<',1:-1L,2:-1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:<[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0: '<',1:-1L,2:1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:<[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0: '<',1:1L,2:-1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:<[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [{0: '<',1:1L,2:1L}],
       eval_  = [False],
       skip   = ['load']),

  dict(lisp   = '[2:<=[7:integer\'1:\xff][7:integer\'1:\xff]]',
       python = [{0:'<=',1:-1L,2:-1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[2:<=[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0:'<=',1:-1L,2:1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[2:<=[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0:'<=',1:1L,2:-1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[2:<=[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [{0:'<=',1:1L,2:1L}],
       eval_  = [True],
       skip   = ['load']),

  dict(lisp   = '[1:=[7:integer\'1:\xff][7:integer\'1:\xff]]',
       python = [{0: '=',1:-1L,2:-1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:=[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0: '=',1:-1L,2:1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:=[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0: '=',1:1L,2:-1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:=[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [{0: '=',1:1L,2:1L}],
       eval_  = [True],
       skip   = ['load']),

  dict(lisp   = '[2:>=[7:integer\'1:\xff][7:integer\'1:\xff]]',
       python = [{0:'>=',1:-1L,2:-1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[2:>=[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0:'>=',1:-1L,2:1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[2:>=[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0:'>=',1:1L,2:-1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[2:>=[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [{0:'>=',1:1L,2:1L}],
       eval_  = [True],
       skip   = ['load']),

  dict(lisp   = '[1:>[7:integer\'1:\xff][7:integer\'1:\xff]]',
       python = [{0: '>',1:-1L,2:-1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:>[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0: '>',1:-1L,2:1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[1:>[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0: '>',1:1L,2:-1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[1:>[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [{0: '>',1:1L,2:1L}],
       eval_  = [False],
       skip   = ['load']),

  dict(lisp   = '[2:!=[7:integer\'1:\xff][7:integer\'1:\xff]]',
       python = [{0:'!=',1:-1L,2:-1L}],
       eval_  = [False],
       skip   = ['load']),
  dict(lisp   = '[2:!=[7:integer\'1:\xff][7:integer\'1:\x01]]',
       python = [{0:'!=',1:-1L,2:1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[2:!=[7:integer\'1:\x01][7:integer\'1:\xff]]',
       python = [{0:'!=',1:1L,2:-1L}],
       eval_  = [True],
       skip   = ['load']),
  dict(lisp   = '[2:!=[7:integer\'1:\x01][7:integer\'1:\x01]]',
       python = [{0:'!=',1:1L,2:1L}],
       eval_  = [False],
       skip   = ['load']),

  # String operators:
  dict(lisp   = '[3:cat[6:decode\'7:Hello, =\'8:encoding\'5:utf-8][6:decode\''
                '6:world!=\'8:encoding\'5:utf-8]]',
       python = [Tuple([
           (0, 'cat'),
           (1, Tuple([
               (0, 'decode'),
               (1, Tuple([(0, 'quote'), (1, 'Hello, ')])),
               (Tuple([(0, 'quote'), (1, 'encoding')]),
                Tuple([(0, 'quote'), (1, 'utf-8')])),
             ])),
           (2, Tuple([
               (0, 'decode'),
               (1, Tuple([(0, 'quote'), (1, 'world!')])),
               (Tuple([(0, 'quote'), (1, 'encoding')]),
                Tuple([(0, 'quote'), (1, 'utf-8')])),
             ])),
         ])],
       eval_  = [u"Hello, world!"],
       skip   = []),
]

class TestCanonicalExpressionPickler(unittest2.TestCase):
  """Test serialization and deserialization of Lisp code to/from Python
  objects using the `CanonicalExpressionPickler` class."""
  __metaclass__ = ScenarioMeta
  _pickler = CanonicalExpressionPickler()
  _environment = Environment(parent=builtinEnvironment)
  _interpreter = BaseInterpreter(pickler=_pickler, environment=_environment)
  class test_dump(PicklerDumpScenarioTest):
    scenarios = SCENARIOS
  class test_load(PicklerLoadScenarioTest):
    scenarios = SCENARIOS
  class test_eval(EvaluateScenarioTest):
    scenarios = SCENARIOS

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
