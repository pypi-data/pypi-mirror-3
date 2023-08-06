#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.base ---------------------------------------------------===
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

from abc import ABCMeta, abstractmethod

from cStringIO import StringIO

__all__ = [
  'BasePickler',
]

class BasePickler(object):
  """A pickler provides a mechanism for serializing Lisp-like code and data
  expressions of a tuple-oriented language into standard, widely-understood
  formats. The `BasePPickler` class provides an abstract interface to these
  serializers."""
  __metaclass__ = ABCMeta

  # Not a typo: SyntaxError is a built-in Python exception, which we want to
  # make a property of this `BasePickler` as well.
  SyntaxError = SyntaxError

  # Various syntax/token constants, used within the load() and dump() methods.
  TUPLE_OPEN      = u"["
  TUPLE_CLOSE     = u"]"
  EVAL_DATA_OPEN  = u"{"
  EVAL_DATA_CLOSE = u"}"
  SEQUENCE_OPEN   = u"("
  SEQUENCE_CLOSE  = u")"

  ASSOCIATION_OPERATOR    = u":"
  QUOTE_OPERATOR          = u"'"
  UNQUOTE_OPERATOR        = u","
  UNQUOTE_SPLICE_OPERATOR = u"`"
  CONSTANT_INDICATOR      = u"#"
  COMMENT_INDICATOR       = u";"

  QUOTE_PROCEDURE          = 'quote'
  UNQUOTE_PROCEDURE        = 'unquote'
  UNQUOTE_SPLICE_PROCEDURE = 'unquote-splice'

  # NOTE: implementors should override `dump()` in preference to `dumps()`, so
  #   that `dump()` does all of the work and `dumps()` calls dump with a
  #   `StringIO` object. In that way pickled expressions can be written to
  #   disk as they are generated, instead of having to generate the entire
  #   pickled expression first, as would be the case when `dumps()` is
  #   overridden.
  def dump(self, ostream, *args, **kwargs):
    """Serialize a Python-represented haiku expression into pickled form and
    write the resulting string to the duck-typed `ostream` file-like
    object."""
    return ostream.write(self.dumps(*args, **kwargs))
  def dumps(self, *args, **kwargs):
    """Serialize a Python-represented haiku expression into pickled form and
    return the result as either a byte- or Unicode-string (as required by the
    pickle format)."""
    ostream = StringIO()
    self.dump(ostream, *args, **kwargs)
    return ostream.getvalue()

  # NOTE: implementors should give preference to overriding `load()` in
  #   preference to `loads()`, for the same reasons explained above for
  #   `dump()` vs. `dumps()`.
  def load(self, istream, *args, **kwargs):
    """Deserializes a haiku expression in pickled form out of the duck-typed
    `istream` file-like object and into Python-represented form."""
    return self.loads(istream.read(), *args, **kwargs)
  def loads(self, expression, *args, **kwargs):
    """Deserializes a haiku expression in pickled form out of the byte- or
    Unicode-string and into Python-represented form."""
    istream = StringIO()
    return self.load(istream, *args, **kwargs)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
