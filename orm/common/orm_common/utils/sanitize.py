import re


def sanitize_symbol_name(value, symbol_meaning=None):
    name_re = re.compile('[A-Za-z0-9_]+$')
    symbol_meaning = symbol_meaning if symbol_meaning else "name"
    return value if name_re.match(value) else "unauthorized " + symbol_meaning
