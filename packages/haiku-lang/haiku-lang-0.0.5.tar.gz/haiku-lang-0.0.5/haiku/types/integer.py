#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.types.integer -------------------------------------------------===
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

"An arbitrary-precision, signed integer type."

__all__ = [
  'Integer',
  'IntegerCompatible',
]

# ===----------------------------------------------------------------------===

# Python standard library, abstract base classes
from abc import ABCMeta

# Python standard library, numeric type hierarchy
import numbers

# `long` is chosen to represent integers as it is an arbitrary-precision type.
# Using a regular Python integer should work fine since Python automatically
# promotes integers in the case of a detected overflows, but that's an
# optimization we can try out in the future when more unit tests are in place.
Integer = long

class IntegerCompatible(object):
  ""
  __metaclass__ = ABCMeta

# `numbers.Integral` is an abstract base class of both `int` and `long`, so it
# is sufficient to check for just `numbers.Integral`:
IntegerCompatible.register(numbers.Integral)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
