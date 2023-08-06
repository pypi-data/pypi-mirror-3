from plywood import Value


def test_some_values():
    '''
    These have already been tested elsewhere, this just tests them wrapped in
    the Value class
    '''
    test = 'var'
    parsed = Value.parseString(test)
    assert parsed['variable'] == "var"
    assert parsed['value'] == 'var'

    test = '123'
    parsed = Value.parseString(test)
    assert parsed['integer'] == "123"
    assert parsed['value'] == '123'

    test = '1.23'
    parsed = Value.parseString(test)
    assert parsed['float'] == "1.23"
    assert parsed['value'] == '1.23'

    test = '0x123'
    parsed = Value.parseString(test)
    assert parsed['hexadecimal'] == "0x123"
    assert parsed['value'] == '0x123'

    test = '0123'
    parsed = Value.parseString(test)
    assert parsed['octal'] == "0123"
    assert parsed['value'] == '0123'

    test = '0o123'
    parsed = Value.parseString(test)
    assert parsed['octal'] == "0o123"
    assert parsed['value'] == '0o123'

    test = '0b1010'
    parsed = Value.parseString(test)
    assert parsed['binary'] == "0b1010"
    assert parsed['value'] == '0b1010'


def test_function_value():
    test = 'var(123)'
    parsed = Value.parseString(test)
    print repr(parsed)
    assert len(parsed) == 3
    assert parsed['expression'][0] == 'var'


def test_list_value():
    test = '[123]'
    parsed = Value.parseString(test)
    print repr(parsed)
    assert len(parsed) == 1
    assert parsed['list'][0] == '123'
