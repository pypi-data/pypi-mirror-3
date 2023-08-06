#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.utils.serialization -------------------------------------------===
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

# Haiku language, type definitions
from haiku.types import *

__all__ = [
  'i2bytearray',
  'i2varnumber',
  's2varstring',
]

# ===----------------------------------------------------------------------===

from bitstring import Bits

def i2bytearray(i):
  "Serializes an integer into a little-endian byte-array."
  i = long(i)
  b = bin(i<0 and -i-1 or i).lstrip('-').rstrip('L')[2:]
  l = 1 + len(b)
  m = l % 8
  l = l + (m and 8-m or 0)
  return Symbol(Bits(intle=i, length=l).bytes)

# ===----------------------------------------------------------------------===

def i2varnumber(i):
  "Serializes an integer to the varnumber format."
  if not i: return ':'
  else:     return Symbol('').join(map(Symbol, [i, ':']))

# ===----------------------------------------------------------------------===

def s2varstring(s):
  "Serializes string to the varstring format."
  if isinstance(s, unicode):
    s = s.encode('utf-8')
  if not s: return Symbol(':')
  else:     return Symbol('').join(map(Symbol, [len(s), ':', s]))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
