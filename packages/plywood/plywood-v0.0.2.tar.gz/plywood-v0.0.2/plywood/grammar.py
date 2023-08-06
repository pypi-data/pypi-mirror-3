from pyparsing import *
L = Literal
ParserElement.verbose_stacktrace = True

# variable
_Variable = Word(alphas + "_", alphanums + "_")
Variable = _Variable('variable')
# values
_Integer = ("0" | Word('123456789', nums))
_Hexadecimal = Combine('0' + CaselessLiteral('x') + Word(hexnums))
_Octal = Combine('0' + Optional(CaselessLiteral('o')) + Word('01234567'))
_Binary = Combine('0' + CaselessLiteral('b') + Word('01'))
_Float = Combine(Optional(_Integer) + '.' + _Integer)
_String = (
        QuotedString(quoteChar="'''", escChar="\\", multiline=True)
      | QuotedString(quoteChar='"""', escChar="\\", multiline=True)
      | QuotedString(quoteChar="'", escQuote="\\'", escChar="\\")
      | QuotedString(quoteChar='"', escQuote='\\"', escChar="\\")
    )
_Infix = oneOf('+ - * /')

Integer = _Integer('integer')
Hexadecimal = _Hexadecimal('hexadecimal')
Octal = _Octal('octal')
Binary = _Binary('binary')
Float = _Float('float')
String = _String('string')
Infix = _Infix('infix')
Number = (Hexadecimal | Octal | Binary | Float | Integer)

Value = Forward()('value')
Expression = Forward()('expression')

Value << (
    Variable
  | Number
  | String
  | Group(Suppress('[') + delimitedList(Expression) + Suppress(']'))('list')
  # | Group(Optional(Variable) + Suppress('(') + delimitedList(Expression) + Suppress(')'))('expression')
  )
Expression << (Value + ZeroOrMore(Infix + Value))
