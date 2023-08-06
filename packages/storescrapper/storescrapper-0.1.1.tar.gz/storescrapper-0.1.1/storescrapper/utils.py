"""
Utility module for functions commonly used by store scripts
"""
from decimal import Decimal


def clean_price_string(price_string):
    """
    Removes most common formatting of a string that represents a price
    leaving it only with its numbers.
    """
    return price_string.replace('$', '').replace('.', '').replace(',', '')


def count_decimals(value):
    """
    Returns the number of decimals in a Decimal value
    e.g.; count_decimals(Decimal("1234.56")) = 2
    """
    return abs(value.as_tuple().exponent)


def format_currency(value, curr='$', sep='.', dp=',',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    curr: optional currency symbol before the sign (may be blank)
    sep: optional grouping separator (comma, period, space, or blank)
    dp: decimal point indicator (comma or period)
    only specify as blank when places is zero
    pos: optional sign for positive numbers: '+', space or blank
    neg: optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator: '-', ')', space or blank

    """

    places = count_decimals(value)

    if not places:
        dp = ''

    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))
