from pytest import raises
from pyparsing import ParseException
from plywood import Hexadecimal


def test_0x123_hexadecimal():
    test = '0x123'
    parsed = Hexadecimal.parseString(test)
    assert len(parsed) == 1
    assert parsed['hexadecimal'] == "0x123"


def test_0X1234567890abcdef_hexadecimal():
    test = '0X1234567890abcdef'
    parsed = Hexadecimal.parseString(test)
    assert len(parsed) == 1
    assert parsed['hexadecimal'] == "0x1234567890abcdef"


def test_0x001234567890abcdef_hexadecimal():
    test = '0x001234567890abcdef'
    parsed = Hexadecimal.parseString(test)
    assert len(parsed) == 1
    assert parsed['hexadecimal'] == "0x001234567890abcdef"


def test_0xfff000_hexadecimal():
    test = '0xfff000'
    parsed = Hexadecimal.parseString(test)
    assert len(parsed) == 1
    assert parsed['hexadecimal'] == "0xfff000"


def test_0xg_fail():
    test = '0xg'
    with raises(ParseException):
        Hexadecimal.parseString(test)
