#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.builtin.baseend -----------------------------------------------===
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

from base64 import (
  urlsafe_b64encode as b64encode,
  urlsafe_b64decode as b64decode)

from haiku.builtin import builtinEnvironment
from haiku.types import *
__all__ = []

# ===----------------------------------------------------------------------===

_b64encode, _b64decode = map(Symbol,
'b64encode   b64decode'.split())

builtinEnvironment[_b64encode] = Procedure(
  params      = Tuple([(1, SymbolCompatible)]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:base64.standard_b64encode(env[1]),
)

builtinEnvironment[_b64decode] = Procedure(
  params      = Tuple([(1, SymbolCompatible)]),
  defaults    = Tuple(),
  ellipsis    = False,
  environment = builtinEnvironment,
  body        = lambda eval_,env:base64.standard_b64decode(env[1]),
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
