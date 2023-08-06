#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.interpreter.base ----------------------------------------------===
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

# Haiku language, type hierarchy
from haiku.types import *

__all__ = [
  'BaseInterpreter',
]

class BaseInterpreter(object):
  "A haiku interpreter state."
  def __init__(self, pickler, environment=None, *args, **kwargs):
    if environment is None:
      raise NotImplementedError
    super(BaseInterpreter, self).__init__(*args, **kwargs)
    self._pickler     = pickler
    self._environment = environment

  # Not a typo: SyntaxError is a built-in Python exception, which we want to
  # make a property of this `BasePickler` as well.
  SyntaxError = SyntaxError

  def read(self, input_):
    "Parse a haiku expression from an input. The type of input is inferred."
    if isinstance(input_, basestring):
      return self._pickler.loads(input_)
    else:
      return self._pickler.load(input_)

  def evaluate(self, expression, environment=None):
    """Evaluate a Python-expressed haiku expression in the context of an
    environment."""
    # To make things easy, the global environment will be used if no
    # environment is specified.
    if None == environment:
      environment = self._environment

    # Handle (trivial) self-evaluating types:
    if isinstance(expression, (
      OmegaCompatible,
      BooleanCompatible,
      IntegerCompatible,
      FractionCompatible,
      UnicodeCompatible)):
      return expression

    # Variable reference (lookup in local environment)
    elif isinstance(expression, SymbolCompatible):
      return environment.resolve(expression)[expression]

    # Handle non-tuple container types, in which the elements of the container
    # are evaluated:
    elif isinstance(expression, (
      SequenceCompatible,
      SetCompatible)):
      return expression.__class__(self.evaluate(elem, environment) for elem in expression)

    # A Matrix is similar to the Set and Sequence container types in that the
    # result of evaluating a matrix is the application of `evaluate` to each
    # of the elements of the matrix. However the multi-dimensional nature of
    # the matrix necessitates that we handle it specially:
    elif isinstance(expression, MatrixCompatible):
      raise NotImplementedError

    # FIXME: figure out what to do with this one
    elif isinstance(expression, RelationCompatible):
      raise NotImplementedError

    # Procedures (user-defined):
    elif isinstance(expression, TupleCompatible):
      if 0 not in expression:
        raise SyntaxError(
          u"expected procedure name in position 0")
      proc = self.evaluate(expression[0], environment)
      expression = Tuple([(key, expression[key])
        for key in filter(lambda key:key!=0, expression.keys())])
      if proc not in ('quote',):
        expression = Tuple([(key, self.evaluate(expression[key], environment))
                            for key in expression])
      if not callable(proc):
        raise self.SyntaxError(
          u"procedure is not callable: %s" % repr(expression[0]))
      return proc(self.evaluate, expression)

    # Procedures (built-in):
    elif callable(expression):
      return expression(self.evaluate, environment)

    else:
      raise ValueError

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
