# vat.py - functions for handling Finnish VAT numbers
# coding: utf-8
#
# Copyright (C) 2012 Arthur de Jong
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

"""ALV nro (Arvonlisäveronumero, Finnish VAT number).

The number is an 8-digit code with a weighted checksum.

>>> compact('FI- 2077474-0')
'20774740'
>>> is_valid('FI 20774740')
True
>>> is_valid('FI 20774741')  # invalid check digit
False
"""

from stdnum.util import clean


def compact(number):
    """Convert the number to the minimal representation. This strips the
    number of any valid separators and removes surrounding whitespace."""
    number = clean(number, ' -').upper().strip()
    if number.startswith('FI'):
        number = number[2:]
    return number


def checksum(number):
    """Calculate the checksum."""
    weights = (7, 9, 10, 5, 8, 4, 2, 1)
    return sum(weights[i] * int(n) for i, n in enumerate(number)) % 11


def is_valid(number):
    """Checks to see if the number provided is a valid VAT number. This
    checks the length, formatting and check digit."""
    try:
        number = compact(number)
    except:
        return False
    return number.isdigit() and len(number) == 8 and checksum(number) == 0
