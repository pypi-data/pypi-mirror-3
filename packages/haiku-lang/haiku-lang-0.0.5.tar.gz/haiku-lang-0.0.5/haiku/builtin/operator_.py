#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.builtin.oeprator ----------------------------------------------===
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

""

import operator

from haiku.builtin import builtinEnvironment
from haiku.pickle import CanonicalExpressionPickler
from haiku.types import *
__all__ = []

# ===----------------------------------------------------------------------===

_and, _or, _xor, _not = map(Symbol,
'&      |     ^     !'.split())

from operator import and_, or_, xor, not_

builtinEnvironment[_and] = Procedure(
  params      = Tuple([
      (1, IntegerCompatible),
      (2, IntegerCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:and_(env[1], env[2]),
)

builtinEnvironment[_or] = Procedure(
  params      = Tuple([
      (1, IntegerCompatible),
      (2, IntegerCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:or_(env[1], env[2]),
)

builtinEnvironment[_xor] = Procedure(
  params      = Tuple([
      (1, IntegerCompatible),
      (2, IntegerCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:xor(env[1], env[2]),
)

builtinEnvironment[_not] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:not_(env[1]),
)

# ===----------------------------------------------------------------------===

_inv, _shift, _rotate = map(Symbol,
'  ~   shift   rotate'.split())

from operator import inv

builtinEnvironment[_inv] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:inv(env[1]),
)

# ===----------------------------------------------------------------------===

_abs, _add, _sub, _div, _mul, _divmod, _pow = map(Symbol,
'abs     +     -     /     *   divmod   pow'.split())

from operator import add, sub, mul, truediv

builtinEnvironment[_add] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
      (2, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:add(env[1], env[2]),
)

builtinEnvironment[_sub] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
      (2, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:sub(env[1], env[2]),
)

def __div(eval_, env):
  if (isinstance(env[1], IntegerCompatible) and
      isinstance(env[2], IntegerCompatible)):
    return Fraction(env[1], env[2])
  else:
    return truediv(env[1], env[2])
builtinEnvironment[_div] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
      (2, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = __div,
)

builtinEnvironment[_mul] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
      (2, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:mul(env[1], env[2]),
)

builtinEnvironment[_divmod] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
      (2, FractionCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:Tuple(zip(
                  ('quotient', 'remainder'),
                  divmod(env[1], env[2]))),
)

def __pow(eval_, env):
  if 3 in env and env[3]:
    return pow(env[1], env[2], env[3])
  else:
    return pow(env[1], env[2])
builtinEnvironment[_pow] = Procedure(
  params      = Tuple([
      (1, FractionCompatible),
      (2, FractionCompatible),
      (3, FractionCompatible),
    ]),
  defaults    = Tuple([
      (3, Fraction(0,1))
    ]),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = __pow,
)

# ===----------------------------------------------------------------------===

_lt, _le, _eq, _ne, _ge, _gt = map(Symbol,
' <   <=    =   !=   >=    >'.split())

builtinEnvironment[_lt] = Procedure(
  params      = Tuple([
      (1, AlphaCompatible),
      (2, AlphaCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:operator.lt(env[1], env[2]),
)

builtinEnvironment[_le] = Procedure(
  params      = Tuple([
      (1, AlphaCompatible),
      (2, AlphaCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:operator.le(env[1], env[2]),
)

builtinEnvironment[_eq] = Procedure(
  params      = Tuple([
      (1, AlphaCompatible),
      (2, AlphaCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:operator.eq(env[1], env[2]),
)

builtinEnvironment[_ne] = Procedure(
  params      = Tuple([
      (1, AlphaCompatible),
      (2, AlphaCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:operator.ne(env[1], env[2]),
)

builtinEnvironment[_gt] = Procedure(
  params      = Tuple([
      (1, AlphaCompatible),
      (2, AlphaCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:operator.gt(env[1], env[2]),
)

builtinEnvironment[_ge] = Procedure(
  params      = Tuple([
      (1, AlphaCompatible),
      (2, AlphaCompatible),
    ]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:operator.ge(env[1], env[2]),
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
