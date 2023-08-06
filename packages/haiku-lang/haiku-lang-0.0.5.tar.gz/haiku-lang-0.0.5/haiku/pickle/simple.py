#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === haiku.pickle.simple -------------------------------------------------===
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

# Haiku language, pickler abstract base class
from .base import BasePickler

__all__ = [
  'SimpleExpressionPickler',
]

# ===----------------------------------------------------------------------===

# s-expression syntax:
#
# TBD...

# Python standard library, Base64 encoding
from base64 import urlsafe_b64encode as b64encode
# Python standard library, iteration tools
from itertools import count, izip
# Python standard library, intrinsic operators
from operator import mul

# LEPL: Recursive descent parser for Python applications
import lepl

class SimpleExpressionPickler(BasePickler):
  """Implements a serialization format for a variant of classic Lisp s-
  expression notation--here renamed “Simple Expressions”--for the Lisp-like,
  tuple-oriented language that is haiku. Simple expressions are the lambda
  calculus expressed through parenthetical prefix notation using a tuple (map/
  dictionary in Python-speak) as the most basic type. Simple expressions are
  meant to be the least complex syntax for for representing haiku code or data
  as Unicode text--a practical compromise between binary-encoded canonical
  expressions and much more human-readable meta expressions.

    >>> from haiku.pickle import SimpleExpressionPickler
    >>> pickler = SimpleExpressionPickler()
    >>> pickler.loads(u'[+ 1 2 3]')
    {0L: {0L: '+', 1L: 1L, 2L: 2L, 3L: 3L}}
    >>> pickler.loads(u'[+ 1 2]\n[print "Hello world!"]')
    {0L: {0L: '+', 1L: 1L, 2L: 2L}, 1L: {0L: 'print', 1L: u'Hello world!'}}
    >>> pickler.dumps({0:'*',1:3,2:{0:'+',1:1,2:6}})
    u'[* 3 [+ 1 6]]'
  """
  # Integers are one or more decimal digits, optionally starting with either a
  # plus or minus sign. (Note: there cannot be any whitespace between the +/-
  # sign and the digits, or else the sign will be misinterpreted as an
  # identifier.)
  INTEGER_SIGN_POSITIVE = set([u"+"])
  INTEGER_SIGN_NEGATIVE = set([u"-"])
  INTEGER_SIGN          = INTEGER_SIGN_POSITIVE.union(INTEGER_SIGN_NEGATIVE)
  INTEGER_DIGIT         = set(u"0123456789")
  INTEGER_SEPARATOR     = set(u"_")

  # Identifiers include what in most other languages would be considered
  # operator syntax, and are collectively here called ‘symbols’. Aside from
  # some select punctuation, it's pretty much anything-goes with respect to
  # non-whitespace, non-control ASCII characters.
  #
  # Note: this has the unintuitive consequence that u"a+b" parses as the
  #   single symbol 'a+b', and as one might expect the separate symbols 'a',
  #   '+', and 'b'. Whitespace is not optional in this case.
  SYMBOL_INITIAL    = set(u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?*+-/%\\&|^_~<=>")
  SYMBOL_SUBSEQUENT = SYMBOL_INITIAL.union(INTEGER_DIGIT)

  def dump(self, ostream, *args, **kwargs):
    """Serializes a Python-represented haiku expression into simple-expression
    notation with Unicode encoding (`'utf-8'` unless overridden with the
    optional keyword parameter `'encoding'`), and writes the resulting string
    to the duck-typed `ostream` file-like object."""
    encoding = kwargs.pop('encoding', 'utf-8')
    # FIXME: `dump()` and `dumps()` should be rewritten so that `dump()` does
    #   all of the work, and `dumps()` calls dump with a `StringIO` object.
    #   That way simple-expressions can be written to disk as they are
    #   generated, instead of having to generate the entire s-expression
    #   string first, as is the case now.
    return ostream.write(self.dumps(*args, **kwargs).encode(encoding))

  def dumps(self, *args):
    """Serialize a Python-represented haiku expression into simple-expression
    notation in a Unicode string.

      >>> from haiku.pickle import SimpleExpressionPickler
      >>> pickler = SimpleExpressionPickler()
      >>> pickler.dumps({0:'*',1:3,2:{0:'+',1:1,2:6}})
      u'[* 3 [+ 1 6]]'
    """
    # `dumps()` is allowed an infinite number of positional arguemnts, each of
    # which must be a Python-represented haiku expression. These are converted
    # into simple-expression notation, then joined together with whitespace.
    if len(args) < 1:
      return u""
    elif len(args) > 1:
      return u" ".join(map(self.dumps, args))

    # Otherwise only one positional arguement is given, and our task is to
    # convert it to s-expression notation.
    return self._serialize(args[0])

  def load(self, istream, **kwargs):
    """Deserializes a haiku expression from an input stream in “Simple
    Expression” notation to Python objects."""
    # FIXME: refactor `loads()` functionality into `load()`, performing
    #        tokenization with a buffer so that large expressions can be
    #        deserialized without having to first load the entire expression
    #        into memory.
    encoding = kwargs.pop('encoding', 'utf-8')
    expression = istream.read().decode(encoding)
    return self.loads(expression, **kwargs)

  def loads(self, expression):
    """Deserializes a haiku expression from a Unicode represented string in
    “Simple Expression” notation to Python objects."""
    return self._matcher.parse(expression)

  def _serialize(self, expression):
    """Translates a Python-represented haiku expression into a Unicode string
    in “Simple Expression” notation."""
    # None/nil/omega value:
    if isinstance(expression, OmegaCompatible):
      return u"".join([self.CONSTANT_INDICATOR, u"nil"])

    # Boolean literals:
    elif isinstance(expression, BooleanCompatible):
      if expression:
        return u"".join([self.CONSTANT_INDICATOR, u"t"])
      else:
        return u"".join([self.CONSTANT_INDICATOR, u"f"])

    # Integral numeric literals:
    elif isinstance(expression, IntegerCompatible):
      return unicode(expression)

    # Rational numeric literals:
    elif isinstance(expression, FractionCompatible):
      return u"".join([
        self.dumps(expression.numerator),
        u"/",
        self.dumps(expression.denominator)])

    # Unicode literals:
    elif isinstance(expression, UnicodeCompatible):
      return u"".join([u'"', expression.encode('unicode_escape')
                                       .replace(u"\"",u"\\\""), u'"'])

    # Symbols literals:
    elif isinstance(expression, SymbolCompatible):
      # An empty symbol is the #empty value
      if not len(expression):
        return u"".join([self.CONSTANT_INDICATOR, u"empty"])

      # A symbol that meets the definition of an identifier is embedded
      # directly:
      if expression[0] in self.SYMBOL_INITIAL:
        if all(c in self.SYMBOL_SUBSEQUENT for c in expression[1:]):
          return unicode(expression)

      # All other symbols are Base64-encoded:
      return u"".join([
        self.TUPLE_OPEN,
        u" ".join([
          u"b64decode",
          u''.join(['\'', b64encode(expression).strip()]),
        ]),
        self.TUPLE_CLOSE])

    # Sets:
    elif isinstance(expression, SetCompatible):
      return u"".join([
        self.TUPLE_OPEN,
        u" ".join([u"set", self.dumps(*sorted(expression))]),
        self.TUPLE_CLOSE])

    # FIXME: implement meta-values

    # Tuples(/maps/dictionaries):
    elif isinstance(expression, TupleCompatible):
      special_pattern = lambda expr:(
        len(expr) == 2 and set(expr.keys()) == set(range(2)))
      # Output special forms:
      if special_pattern(expression):
        if expression[0] == self.QUOTE_PROCEDURE:
          #if (isinstance(expression[1], TupleCompatible) and
          #    all(special_pattern(expression[1][key]) and
          #        expression[1][key][0] == self.UNQUOTE_PROCEDURE
          #        for key in expression[1].keys())):
          #  return u"".join([
          #    self.EVAL_DATA_OPEN,
          #    self.dumps(expression[1]),
          #    self.EVAL_DATA_CLOSE])
          return u"".join([self.QUOTE_OPERATOR, self.dumps(expression[1])])
        if expression[0] == self.UNQUOTE_PROCEDURE:
          return u"".join([self.UNQUOTE_OPERATOR, self.dumps(expression[1])])
        if expression[0] == self.UNQUOTE_SPLICE_PROCEDURE:
          return u"".join([self.UNQUOTE_SPLICE_OPERATOR, self.dumps(expression[1])])

      args = []
      kwargs_keys = expression.keys()
      for key in count():
        if key in kwargs_keys:
          kwargs_keys.remove(key)
          args.append(expression[key])
        else:
          break
      return u"".join([
        self.TUPLE_OPEN,
        u"".join([
          self.dumps(*args),
          (len(args) and len(kwargs_keys)) and u" " or u"",
          u" ".join(
            u"".join([
              self.dumps(key),
              self.ASSOCIATION_OPERATOR,
              self.dumps(expression[key]),
            ]) for key in sorted(kwargs_keys))]),
        self.TUPLE_CLOSE])

    # Relations:
    elif isinstance(expression, RelationCompatible):
      raise NotImplementedError

    # Sequences(/lists):
    elif isinstance(expression, SequenceCompatible):
      return u"".join([
        self.SEQUENCE_OPEN,
        self.dumps(*expression),
        self.SEQUENCE_CLOSE])

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
    super(SimpleExpressionPickler, self).__init__(*args, **kwargs)

    # “Whitespace” is any formatting characters (spaces, newlines, comments,
    # etc.) which are used to separate tokens, but are not represented except
    # implicitly in the Python representation.
    # FIXME: add support for any Unicode whitespace or newline character
    Whitespace = (lepl.Any(u"\t\n\u000b\u000c\r ") |
      (lepl.Literal(u";") &
       lepl.AnyBut(lepl.Newline())[0:] &
       (lepl.Newline() | lepl.Lookahead(lepl.Eos()))))

    # Symbols are a stand-in type for both identifiers and operators (<, =, &,
    # etc.).
    # FIXME: add support for hex strings a la D
    _Identifier = lambda lexemes:Symbol(u"".join(lexemes).encode('utf-8'))
    Identifier = (
      lepl.Any(self.SYMBOL_INITIAL) &
      lepl.Any(self.SYMBOL_SUBSEQUENT)[0:]) > _Identifier

    # FIXME: add support for binary, octal, hex, and perhaps other integer
    #   representations
    _UnsignedInteger = lambda lexemes:Integer(u"".join(
      filter(
        lambda lexeme:lexeme not in self.INTEGER_SEPARATOR,
        lexemes)))
    UnsignedInteger = (
        lepl.Any(self.INTEGER_DIGIT) |
        lepl.Any(self.INTEGER_SEPARATOR)
      )[1:] > _UnsignedInteger

    _IntegerSign = (lambda lexeme:
      lexeme in self.INTEGER_SIGN_NEGATIVE and Integer(-1)
                                            or Integer(1))
    IntegerSign = lepl.Any(self.INTEGER_SIGN) >> _IntegerSign

    _SignedInteger = lambda parts:reduce(mul, parts)
    SignedInteger = (
      lepl.Optional(IntegerSign) &
      UnsignedInteger) > _SignedInteger

    Integral = SignedInteger

    # Rational literals must not include any whitespace between the numerator,
    # the divider, and the denominator, otherwise the grammer would be
    # ambiguous.
    # FIXME: consider supporting decimal literals as fractions
    _Rational = lambda args:Fraction(*args)
    Rational = (
      SignedInteger &
      ~lepl.Literal(u"/") &
      UnsignedInteger) > _Rational

    # We rely upon Python's Unicode escape capability for parsing Unicode
    # strings:
    # FIXME: consider supporting smart quotes and any other Unicode quote
    #   pairings.
    _UnicodeString = lambda args:args and Unicode(*args).decode('unicode_escape') or Unicode(u"")
    UnicodeString = lepl.String(quote=u'"', escape=u"\\") > _UnicodeString

    # Whitespace is *not* required between tokens, as long as it does not
    # result in any ambiguity.
    with lepl.Separator(~Whitespace[0:]):
      # Expression is used recursively, so we declare it up front without
      # being required to define it:
      Expression = lepl.Delayed()

      # Named constants are used for the `Omega` value (nil/None), and the
      # Boolean values `True` and `False`.
      def _Constant(symbol):
        symbol = symbol.lower()
        if symbol in ('nil',):
          return Omega()
        if symbol in ('f','false'):
          return Boolean(False)
        if symbol in ('t','true'):
          return Boolean(True)
        if symbol in ('empty',):
          return Symbol('')
        raise self.SyntaxError(
          u"unrecognized constant name: %s" % repr(symbol))
      Constant = (~lepl.Literal(u"#") & Identifier) >> _Constant

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
        Expression &
        ~lepl.Literal(self.ASSOCIATION_OPERATOR) &
        Expression) | Expression) > _KeywordExpression

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
        TupleSyntax | EvalDataSyntax | SequenceSyntax | UnicodeString |
        Rational | Integral | Constant | Identifier)

      # ...and our overall grammar: zero or more Expression's optionally
      # separated by whitespace.
      Syntax = Expression[0:] & ~lepl.Eos()

    # Save the `Syntax` matcher for use by other methods:
    self._matcher = Syntax

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
