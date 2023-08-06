#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.canonical ----------------------------------------------===
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

# Haiku language, type definitions
from haiku.types import *

from .base import BasePickler

__all__ = [
  'CanonicalExpressionPickler',
]

# ===----------------------------------------------------------------------===

# c-expression syntax:
#
#  <c-tuple>:: “[” <c-expr>* “]”
#   <c-expr>:: <c-part> | “'” <c-expr> | “,” <c-expr> | “`” <c-expr>
#   <c-part>:: <atom> | <c-expr>
#     <atom>:: <decimal> “:” [octet array of <decimal> length]
#  <decimal>:: <nzddigit> <ddigit>*
# <nzddigit>:: “1” | “2” | “3” | “4” | “5” | “6” | “7” | “8” | “9”
#   <ddigit>:: “0” | <nzddigit>
#
# That's it!

# Python standard library,
from copy import copy

# Python standard library, iteration tools
from itertools import count, izip

# LEPL: Recursive descent parser for Python applications
import lepl
from lepl.core.dynamic import IntVar as lepl_IntVar

from haiku.utils.serialization import i2bytearray, i2varnumber, s2varstring

class CanonicalExpressionPickler(BasePickler):
  ""
  ASSOCIATION_OPERATOR = u"="

  def dumps(self, *args):
    """Serialize a Python-represented haiku expression into canonical-
    expression notation.

      >>> from haiku.pickle import CanonicalExpressionPickler
      >>> pickler = CanonicalExpressionPickler()
      >>> pickler.dumps({0:'*',1:3,2:{0:'+',1:1,2:6}})
      '(1:*(7:integer1:3)(1:+(7:integer:1:17:integer:1:6))'
    """
    # `dumps()` is allowed an infinite number of positional arguemnts, each of
    # which must be a Python-represented haiku expression. These are converted
    # into simple-expression notation, then joined together.
    if len(args) < 1:
      return ''
    elif len(args) > 1:
      return ''.join(map(self.dumps, args))

    # Otherwise only one positional arguement is given, and our task is to
    # convert it to s-expression notation.
    return self._serialize(args[0])

  def loads(self, expression):
    """Deserializes a haiku expression from a Unicode represented string in
    “Canonical Expression” notation to Python objects."""
    return self._matcher.parse(expression)

  def _serialize(self, expression):
    """Translates a Python-represented haiku expression into a byte string
    in “Canonical Expression” notation."""
    # None/nil/omega value:
    if isinstance(expression, OmegaCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('nil'),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Boolean literals:
    elif isinstance(expression, BooleanCompatible):
      if expression:
        return ''.join([
          self.TUPLE_OPEN.encode('utf-8'),
          s2varstring('true'),
          self.TUPLE_CLOSE.encode('utf-8')])
      else:
        return ''.join([
          self.TUPLE_OPEN.encode('utf-8'),
          s2varstring('false'),
          self.TUPLE_CLOSE.encode('utf-8')])

    # Integral numeric literals:
    elif isinstance(expression, IntegerCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('integer'),
        self.QUOTE_OPERATOR.encode('utf-8'),
        s2varstring(expression and i2bytearray(expression) or ''),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Rational numeric literals:
    elif isinstance(expression, FractionCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('rational'),
        self._serialize(expression.numerator),
        self._serialize(expression.denominator),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Unicode literals:
    elif isinstance(expression, UnicodeCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('decode'),
        self.QUOTE_OPERATOR.encode('utf-8'),
        s2varstring(expression.encode('utf-8')),
        self.ASSOCIATION_OPERATOR.encode('utf-8'),
        self.QUOTE_OPERATOR.encode('utf-8'),
        s2varstring('encoding'),
        self.QUOTE_OPERATOR.encode('utf-8'),
        s2varstring('utf-8'),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Byte-array literals:
    elif isinstance(expression, SymbolCompatible):
      return s2varstring(expression)

    # Sets:
    elif isinstance(expression, SetCompatible):
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        s2varstring('set'),
        ''.join(self._serialize(elem) for elem in sorted(expression)),
        self.TUPLE_CLOSE.encode('utf-8')])

    # FIXME: implement meta-values

    # Tuples(/maps/dictionaries):
    elif isinstance(expression, TupleCompatible):
      special_pattern = lambda expr:(
        len(expr) == 2 and set(expr.keys()) == set(range(2)))
      # Output special forms:
      if special_pattern(expression):
        if expression[0] == self.QUOTE_PROCEDURE:
          if (isinstance(expression[1], TupleCompatible) and
              all(special_pattern(expression[1][key]) and
                  expression[1][key][0] == self.UNQUOTE_PROCEDURE
                  for key in expression[1])):
            return ''.join([
              self.EVAL_DATA_OPEN.encode('utf-8'),
              self._serialize(Tuple((key, expression[1][key][1])
                                    for key in expression[1]))[1:-1],
              self.EVAL_DATA_CLOSE.encode('utf-8')])
          return ''.join([
            self.QUOTE_OPERATOR.encode('utf-8'),
            self._serialize(expression[1])])
        if expression[0] == self.UNQUOTE_PROCEDURE:
          return ''.join([
            self.UNQUOTE_OPERATOR.encode('utf-8'),
            self._serialize(expression[1])])
        if expression[0] == self.UNQUOTE_SPLICE_PROCEDURE:
          return ''.join([
            self.UNQUOTE_SPLICE_OPERATOR.encode('utf-8'),
            self._serialize(expression[1])])

      args = []
      kwargs_keys = expression.keys()
      for key in count():
        if key in kwargs_keys:
          kwargs_keys.remove(key)
          args.append(expression[key])
        else:
          break
      return ''.join([
        self.TUPLE_OPEN.encode('utf-8'),
        ''.join([
          ''.join(self._serialize(arg) for arg in args),
          ''.join(
            ''.join([
              self.ASSOCIATION_OPERATOR.encode('utf-8'),
              self._serialize(key),
              self._serialize(expression[key]),
            ]) for key in sorted(kwargs_keys))]),
        self.TUPLE_CLOSE.encode('utf-8')])

    # Relations:
    elif isinstance(expression, RelationCompatible):
      raise NotImplementedError

    # Sequences(/lists):
    elif isinstance(expression, SequenceCompatible):
      return ''.join([
        self.SEQUENCE_OPEN.encode('utf-8'),
        ''.join(self._serialize(elem) for elem in expression),
        self.SEQUENCE_CLOSE.encode('utf-8')])

    # Matrices:
    elif isinstance(expression, MatrixCompatible):
      raise NotImplementedError

    # Procedures(/lambdas):
    elif isinstance(expression, Procedure):
      raise NotImplementedError

    # That's it! We should have matched one of the previous cases and returned
    # already if we were a valid Python-represented haiku expression. So we
    # can assume the caller passed us something in error and report the
    # problem:
    raise ValueError(
      u"unrecognized input (not a valid expression): '%s'" % repr(expression))

  def __init__(self, *args, **kwargs):
    "Sets up a parser using the LEPL package."
    super(CanonicalExpressionPickler, self).__init__(*args, **kwargs)

    Expression = lepl.Delayed()

    _UnsignedInteger = lambda digits:int(''.join(digits) or '0')
    UnsignedInteger = (
        lepl.Optional(lepl.Any('123456789') &
                      lepl.Any('0123456789')[:]) &
        ~lepl.Literal(':')
      ) > _UnsignedInteger

    _ByteArray = lambda bytes:Symbol(''.join(bytes))
    _ByteArrayLength = lepl_IntVar()
    _ByteArrayHeader = lepl.Apply(UnsignedInteger, _ByteArrayLength.setter())
    _ByteArrayBody   = lepl.Repeat(lepl.Any(), stop=_ByteArrayLength, add_=True)
    ByteArray = (
      ~_ByteArrayHeader &
      _ByteArrayBody) > _ByteArray
    ByteArray.config.no_compile_to_regexp()

    # Special forms for quoting:
    _QuoteSyntax = lambda expr:Tuple([
      (0, self.QUOTE_PROCEDURE),
      (1, expr)])
    QuoteSyntax = (
      ~lepl.Literal(self.QUOTE_OPERATOR) & Expression) >> _QuoteSyntax

    _UnquoteSyntax = lambda expr:Tuple([
      (0, self.UNQUOTE_PROCEDURE),
      (1, expr)])
    UnquoteSyntax = (
      ~lepl.Literal(self.UNQUOTE_OPERATOR) & Expression) >> _UnquoteSyntax

    _UnquoteSpliceSyntax = lambda expr:Tuple([
      (0, self.UNQUOTE_SPLICE_PROCEDURE),
      (1, expr)])
    UnquoteSpliceSyntax = (
      ~lepl.Literal(self.UNQUOTE_SPLICE_OPERATOR) & Expression) >> _UnquoteSyntax

    # A keyword expression is a component of the tuple definition: a mapping
    # of one data to another (the key/value pair).
    _KeywordExpression = lambda parts:len(parts)-1 and tuple(parts) or parts[0]
    KeywordExpression = ((
        ~lepl.Literal(self.ASSOCIATION_OPERATOR.encode('utf-8'))
        & Expression & Expression
      ) | Expression) > _KeywordExpression

    # The creation of tuple values is a little tricky as keys may be
    # specified either implicitly (by position) or explicitly.
    def icount(*args, **kwargs):
      _iter = count(*args, **kwargs)
      for i in _iter:
        yield Integer(i)
    def _TupleSyntax(parts):
      # (Remember, Python's `tuple` is quite different from haiku's `Tuple`)
      kwargs = filter(lambda arg:isinstance(arg, tuple), parts)
      args   = filter(lambda arg:arg not in kwargs, parts)
      tuple_ = Tuple(kwargs)
      if len(kwargs) != len(tuple_):
        raise self.SyntaxError(
          u"duplicate keys in keyword arguments")
      tuple_ = Tuple([x for x in izip(icount(), args)] + kwargs)
      if len(parts) != len(tuple_):
        dups = filter(lambda x:x in tuple_, xrange(len(args)))
        raise self.SyntaxError(
          u"redundant parameter(s) specified positionally and as keyword arguments")
      return tuple_
    TupleSyntax = (
      ~lepl.Literal(self.TUPLE_OPEN) &
      KeywordExpression[0:] &
      ~lepl.Literal(self.TUPLE_CLOSE)) > _TupleSyntax

    # Eval-data special form:
    def _EvalDataSyntax(parts):
      tuple_ = _TupleSyntax(parts)
      tuple_ = Tuple([(key, _UnquoteSyntax(value)) for key, value in tuple_.items()])
      tuple_ = Tuple([(0, self.QUOTE_PROCEDURE), (1, tuple_)])
      return tuple_
    EvalDataSyntax = (
      ~lepl.Literal(self.EVAL_DATA_OPEN) &
      KeywordExpression[0:] &
      ~lepl.Literal(self.EVAL_DATA_CLOSE)) > _EvalDataSyntax

    # Sequence special form:
    _SequenceSyntax = lambda args:Sequence(args)
    SequenceSyntax = (
      ~lepl.Literal(self.SEQUENCE_OPEN) &
      Expression[0:] &
      ~lepl.Literal(self.SEQUENCE_CLOSE)) > _SequenceSyntax

    # Now that we've defined each component, we can go back and complete
    # Expression's definition:
    Expression += (QuoteSyntax | UnquoteSyntax | UnquoteSpliceSyntax |
      TupleSyntax | EvalDataSyntax | SequenceSyntax | ByteArray)

    # ...and our overall grammar: zero or more Expression's optionally
    # separated by whitespace.
    Syntax = Expression[0:] & ~lepl.Eos()

    # Save the `Syntax` matcher for use by other methods:
    self._matcher = Syntax

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
