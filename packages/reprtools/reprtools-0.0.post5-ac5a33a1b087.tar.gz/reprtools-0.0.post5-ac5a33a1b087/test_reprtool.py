from reprtools import FormatRepr, SelfFormatter

def test_format_repr():
    r = FormatRepr("{name}")
    rep = repr(r)
    assert rep == 'FormatRepr(\'{name}\')'
