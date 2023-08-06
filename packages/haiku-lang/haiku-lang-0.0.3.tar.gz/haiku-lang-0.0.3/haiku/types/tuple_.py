#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.types.tuple_ --------------------------------------------------===
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

"""A *tuple* is a set of ordered pairs or *attributes* of the form
`<A, T, V>`, where: `A` is the name of an attribute of the tuple, and no two
distinct attributes have the same name; `T` is the declared type of the
attribute; and `V` is the attribute value, an instance of (a subtype of) `T`.
In other words, a *tuple* as defined by the relational model of Edgar Codd.

Sequences(/lists) can be constructed out of tuples(/maps/dictionaries) if one
observes that a list is in fact a mapping of indices to values. For that
reason tuples are the most fundamental type in haiku, a tuple-oriented(/map-
based) generalization of Lisp. Tuples map nicely onto the Python `dict` type
for our purposes."""

__all__ = [
  'Tuple',
  'FrozenTuple',
  'TupleCompatible',
]

# ===----------------------------------------------------------------------===

# Python standard library, abstract base classes
from abc import ABCMeta

Tuple = dict
from haiku.utils.frozendict import frozendict as FrozenTuple

class TupleCompatible(object):
  ""
  __metaclass__ = ABCMeta
TupleCompatible.register(Tuple)
TupleCompatible.register(FrozenTuple)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
