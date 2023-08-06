#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.types.relation ------------------------------------------------===
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

"""A relation value (relation for short) consists of a *heading* and a *body*,
where:
  1) The heading of the relation is a (possibly empty) set of ordered pairs or
     *attributes* of the form `<A, T>, where: is the name of an attribute, and
     no two distinct attributes have the same name; and T is the declared type
     of the attribute.
  2) The body of of the relation is a (possibly empty) set of tuples, all
     having that same heading.

In other words, a *relation* as defined by the relational model of Edgar
Codd."""

__all__ = [
  'Relation',
  'RelationCompatible',
]

# ===----------------------------------------------------------------------===

# Python standard library, abstract base classes
from abc import ABCMeta

# FIXME: actually implement the Relation type, using the pandas package if
#   available, otherwise falling back on a simple/naïve pure-python
#   implementation.

class Relation(object):
  ""
  pass

class RelationCompatible(object):
  ""
  __metaclass__ = ABCMeta
RelationCompatible.register(Relation)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
