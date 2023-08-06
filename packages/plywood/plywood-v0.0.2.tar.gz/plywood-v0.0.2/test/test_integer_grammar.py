from plywood import Integer


def test_123_integer():
    test = '123'
    parsed = Integer.parseString(test)
    assert len(parsed) == 1
    assert parsed['integer'] == "123"


def test_0_integer():
    test = '0'
    parsed = Integer.parseString(test)
    assert len(parsed) == 1
    assert parsed['integer'] == "0"


def test_456_integer():
    test = '456'
    parsed = Integer.parseString(test)
    assert len(parsed) == 1
    assert parsed['integer'] == "456"


def test_789_integer():
    test = '789'
    parsed = Integer.parseString(test)
    assert len(parsed) == 1
    assert parsed['integer'] == "789"
