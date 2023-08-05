#    math115utils -- A115's Python Math Utilities
#    Copyright (C) 2011  A115 Ltd.
#
#    This library is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this library.  If not, see <http://www.gnu.org/licenses/>.
#

from random import randint
from decimal import Decimal

#
# A generic exception to use when we want to indicate that 
# the provided input is out of the supported range. 
#
class OutOfRangeError(Exception):
    pass

#
# Python class for creating infix notation operators. E.g.:
#
# >>> def _pct(a, b):
# ...     return a*b / 100.0
# >>> pct = Infix(pct)
# >>> 15 |pct| 180
# 27.0
#
class Infix(object):
    def __init__(self, f):
        self.function = f
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, v1, v2):
        return self.function(v1, v2)

#
# convert anything to a Decimal
#
dcml = lambda x: Decimal(str(x))


#
# Calculate p percent from x (as infix operator)
#
@Infix
def pct(p, x): 
    return dcml(p)*dcml(x)/dcml(100)

#
# Mark a value v up by p percent, eg: 
# >>> mark_up(10, 80):
# 88
#
mark_up = lambda p,v: dcml(v) + dcml(p)*dcml(v)/dcml(100)

#
# Mark a value v down by p percent, eg: 
# >>> mark_down(10, 80):
# 72
#
mark_down = lambda p,v: mark_up(dcml(-1)*dcml(p), v)

#
# The function closed_interval_overlap returns True if the 
# intervals [f1,f2] and [s1,s2] overlap
# 
def closed_interval_overlap(f1, f2, s1, s2):
    return any([(s1 <= f1 <= s2),
                (s1 <= f2 <= s2),
                (f1 <= s1 <= f2),
                (f1 <= s2 <= f2),
                ])
#
# int_to_roman converts an integer to roman numeral.  The 
# integer must be in the range 1 .. 4000
#
def int_to_roman(n):
    Rom={}
    Rom["M"] = 1000
    Rom["CM"] = 900
    Rom["D"] = 500
    Rom["CD"] = 400
    Rom["C"] = 100
    Rom["XC"] = 90
    Rom["L"] = 50
    Rom["XL"] = 40
    Rom["X"] = 10
    Rom["IX"] = 9
    Rom["V"] = 5
    Rom["IV"] = 4
    Rom["I"] = 1
    RomSeq = ( "M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I" )
    result=""
    if not isinstance(n, int):
        raise TypeError
    if n < 1 or n > 4000:
        raise OutOfRangeError
    for i in RomSeq:
        while Rom[i] <= n:
            result = result + i
            n = n - Rom[i]
    return result

#
# Convert a float or a european style float (with decimal comma) to 
# a formatted string with a precision of two decimal digits and a 
# decimal dot. If the float can not be converted, return "0.00".  
#

def float_or_zero(value):
    try:
        return "%.2f" % float(str(value).replace(',', '.'))
    except:
        return "0.00"
