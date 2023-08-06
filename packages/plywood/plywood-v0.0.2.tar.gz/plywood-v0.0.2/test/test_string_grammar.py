from pytest import raises
from pyparsing import ParseException
from plywood import String


def test_single_quoted_string():
    test = "'single_quoted'"
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "single_quoted"


def test_single_quoted_slash_string():
    test = "'single_quoted_\\slash'"
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "single_quoted_\\slash"


def test_single_quoted_escaped_string():
    test = "'single_quoted\\'escaped'"
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == 'single_quoted\'escaped'


def test_double_quoted_string():
    test = '"double_quoted"'
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "double_quoted"


def test_double_quoted_slash_string():
    test = '"double_quoted_\\slash"'
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "double_quoted_\\slash"


def test_double_quoted_escaped_string():
    test = '"double_quoted\\\"escaped"'
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "double_quoted\"escaped"


def test_triple_single_quoted_string():
    test = """'''triple
single
quoted'''"""
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "triple\nsingle\nquoted"


def test_trible_double_quoted_string():
    test = '''"""triple
double
quoted"""'''
    parsed = String.parseString(test)
    assert len(parsed) == 1
    assert parsed['string'] == "triple\ndouble\nquoted"


def test_no_quotes_fail():
    test = 'no_quotes'
    with raises(ParseException):
        String.parseString(test)


def test_no_closing_single_quote_fail():
    test = "'no_closing_single_quote"
    with raises(ParseException):
        String.parseString(test)


def test_no_closing_double_quote_fail():
    test = '"no_closing_double_quote'
    with raises(ParseException):
        String.parseString(test)
