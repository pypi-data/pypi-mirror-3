from plywood import Infix


def test_substract_infix():
    test = '-'
    parsed = Infix.parseString(test)
    assert len(parsed) == 1
    assert parsed['infix'] == "-"


def test_add_infix():
    test = '+'
    parsed = Infix.parseString(test)
    assert len(parsed) == 1
    assert parsed['infix'] == "+"


def test_division_infix():
    test = '/'
    parsed = Infix.parseString(test)
    assert len(parsed) == 1
    assert parsed['infix'] == "/"


def test_multiplication_infix():
    test = '*'
    parsed = Infix.parseString(test)
    assert len(parsed) == 1
    assert parsed['infix'] == "*"
