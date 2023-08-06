from pytest import raises
from pyparsing import ParseException
from plywood import Binary


def test_0b101_binary():
    test = '0b101'
    parsed = Binary.parseString(test)
    assert len(parsed) == 1
    assert parsed[0] == "0b101"


def test_0B101_binary():
    test = '0B101'
    parsed = Binary.parseString(test)
    assert len(parsed) == 1
    assert parsed[0] == "0b101"


def test_0b001_binary():
    test = '0b001'
    parsed = Binary.parseString(test)
    assert len(parsed) == 1
    assert parsed[0] == "0b001"


def test_0B111000_binary():
    test = '0B111000'
    parsed = Binary.parseString(test)
    assert len(parsed) == 1
    assert parsed[0] == "0b111000"


def test_0b2_fail():
    test = '0b2'
    with raises(ParseException):
        Binary.parseString(test)
