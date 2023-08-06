#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.types.omega ---------------------------------------------------===
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

"""Provides the Omega conceptual dummy type which is the proper subtype of
every type except itself, and a proper supertype of none."""

__all__ = [
  'Omega',
  'OmegaCompatible',
]

# ===----------------------------------------------------------------------===

# Python standard library, abstract base classes
from abc import ABCMeta

class Omega(object):
  """A conceptual dummy type which is the proper subtype of every type except
  itself, and a proper supertype of none. Arguing whether any value exists for
  the `Omega` is a bit like arguing how many angels could fit on the head of a
  pin. For practical purposes, the omega type has one value representing the
  absence of value (not unlike the Python keyword `None`), and all instances of
  the omega type are this value."""
  def __new__(cls, *arg, **kwargs):
    return None

class OmegaCompatible(object):
  ""
  __metaclass__ = ABCMeta

# There shouldn't be any instances of the Omega class, ever, but the following
# allows `issubclass(Omega, OmegaCompatible)` to be true:
OmegaCompatible.register(Omega)

# Amazingly, the following does work, making
# `isinstance(None, OmegaCompatible)` true:
OmegaCompatible.register(type(None))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
