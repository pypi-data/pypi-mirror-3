from pytest import raises
from pyparsing import ParseException
from plywood import Variable


def test_var_variable():
    test = 'var'
    parsed = Variable.parseString(test)
    assert parsed['variable'] == "var"


def test_1a_variable():
    test = '_1a'
    parsed = Variable.parseString(test)
    assert parsed['variable'] == "_1a"


def test_underscore_variable():
    test = '____'
    parsed = Variable.parseString(test)
    assert parsed['variable'] == "____"


def test_alphanumeric_variable():
    test = 'abc123'
    parsed = Variable.parseString(test)
    assert parsed['variable'] == "abc123"


def test_numeric_fail():
    test = '123abc'
    with raises(ParseException):
        Variable.parseString(test)


def test_spaces_fail():
    test = '123abc'
    with raises(ParseException):
        Variable.parseString(test)
