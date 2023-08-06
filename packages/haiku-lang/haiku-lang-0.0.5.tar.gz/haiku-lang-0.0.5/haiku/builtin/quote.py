#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.builtin.quote -------------------------------------------------===
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

from haiku.builtin import builtinEnvironment
from haiku.types import *
__all__ = []

# ===----------------------------------------------------------------------===

_quote, _unquote, _unquote_splice = map(Symbol,
'quote   unquote   unquote-splice'.split())

def do_quote(eval_, obj, level=0):
  if isinstance(obj, TupleCompatible):
    for key, value in obj.items():
      if isinstance(value, TupleCompatible) and 0 in value: 
        if value[0] in (_quote,):
          obj[key] = do_quote(eval_, value, level+1)
        if value[0] in (_unquote, _unquote_splice):
          if level:
            obj[key] = do_quote(eval_, value, level-1)
          else:
            obj[key] = eval_(value, env)
  return obj
builtinEnvironment[_quote] = Procedure(
  params      = Tuple([(1, AlphaCompatible)]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:do_quote(eval_,env[1]),
)

def do_unquote(eval_, env):
  raise SyntaxError(
    u"unquote not allowed outside of enclosing quote")
builtinEnvironment[_unquote] = Procedure(
  params      = Tuple([(1, AlphaCompatible)]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = do_unquote,
)

def do_unquote_splice(eval_, env):
  raise SyntaxError(
    u"unquote-splice not allowed outside of enclosing quote")
builtinEnvironment[_unquote_splice] = Procedure(
  params      = Tuple([(1, TupleCompatible)]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = do_unquote_splice,
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
