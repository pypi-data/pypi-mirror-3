from plywood import Float


def test_123_float():
    test = '1.23'
    parsed = Float.parseString(test)
    assert len(parsed) == 1
    assert parsed['float'] == "1.23"


def test_0_float():
    test = '0.0'
    parsed = Float.parseString(test)
    assert len(parsed) == 1
    assert parsed['float'] == "0.0"


def test_456_float():
    test = '.456'
    parsed = Float.parseString(test)
    assert len(parsed) == 1
    assert parsed['float'] == ".456"
