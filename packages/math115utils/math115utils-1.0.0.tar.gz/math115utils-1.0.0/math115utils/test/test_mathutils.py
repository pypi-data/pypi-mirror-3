import unittest

#
# Define some utility functions first, which will be 
# useful for testing.  
# 

from decimal import Decimal
from math115utils import OutOfRangeError

def _pct(a, b): 
    return a*b / 100.0

def _isa(a, b):
    return a.__class__ == b.__class__

def _is_in(a, b):
    return b.has_key(a)

#
# Now on to the actual tests...
#

class TestMathUtils(unittest.TestCase):
    def setUp(self):
        self.simple_dict = {'a': 1, 'b': 2, 'c':3}

from math115utils import Infix
class TestInfix(TestMathUtils):

    def test_infix_with_pct(self):
        pct = Infix(_pct)
        self.assertEqual(15 |pct| 80, 12.0)
        self.assertEqual(15 <<pct>> 80, 12.0)

    def test_infix_with_isa(self):
        isa = Infix(_isa)
        self.assertTrue([1,2,3] |isa| [])
        self.assertTrue([1,2,3] <<isa>> [])
        self.assertFalse(5 |isa| [])

    def test_infix_with_is_in(self):
        is_in = Infix(_is_in)
        self.assertTrue('b' |is_in| self.simple_dict)
        self.assertFalse('q' |is_in| self.simple_dict)

from math115utils import dcml
class TestDcml(TestMathUtils):

    def test_dcml_with_int(self):
        self.assertIsInstance(dcml(5), Decimal)
        self.assertEqual(dcml(123), Decimal("123.00"))
        self.assertEqual(dcml(-9999), Decimal("-9999.00"))

    def test_dcml_with_float(self):
        self.assertIsInstance(dcml(5.0), Decimal)
        self.assertEqual(dcml(0.123), Decimal("0.123"))
        self.assertEqual(dcml(-99999.99), Decimal("-99999.99"))

    def test_dcml_with_string(self):
        self.assertIsInstance(dcml("5.0"), Decimal)
        self.assertEqual(dcml("0.00000000000123"), Decimal("0.00000000000123"))
        self.assertEqual(dcml("-9999999999999999999999.0000000000000001"), Decimal("-9999999999999999999999.0000000000000001"))
    
    def test_dcml_with_decimal(self):
        self.assertIsInstance(dcml(Decimal("5.0")), Decimal)
        self.assertEqual(dcml(Decimal("-0.00000000000123")), Decimal("-0.00000000000123"))
        self.assertEqual(dcml(Decimal("99999.99")), Decimal("99999.99"))

    def test_dcml_with_non_number(self):
        from decimal import InvalidOperation
        with self.assertRaises(InvalidOperation):
            error = dcml('aba')

from math115utils import pct
class TestPct(TestMathUtils):

    def test_pct_as_prefix(self):
        self.assertEqual(pct(15, 80), 12.0)

    def test_pct_as_infix(self):
        self.assertEqual("1.34" |pct| 9000.03, Decimal("120.600402"))

from math115utils import mark_up
class TestMarkUp(TestMathUtils):

    def test_mark_up_positive_value_by_positive_percentage(self):
        self.assertEqual(mark_up(10, 80), 88)
        self.assertEqual(mark_up("0.0000001", "0.04"), Decimal("0.04000000004"))

    def test_mark_up_positive_value_by_negative_percentage(self):
        self.assertEqual(mark_up(-10, 80), 72)
        self.assertEqual(mark_up("-0.0000001", "0.04"), Decimal("0.03999999996"))

    def test_mark_up_by_zero(self):
        self.assertEqual(mark_up(0, 999), 999)
        self.assertEqual(mark_up(0, -999), -999)
        self.assertEqual(mark_up(0, "0.000001"), Decimal("0.000001"))

    def test_mark_up_negative_value_by_positive_percentage(self):
        self.assertEqual(mark_up(10, -80), -88)
        self.assertEqual(mark_up("0.0000001", "-0.04"), Decimal("-0.04000000004"))
    
    def test_mark_up_negative_value_by_negative_percentage(self):
        self.assertEqual(mark_up(-10, -80), -72)
        self.assertEqual(mark_up("-0.0000001", "-0.04"), Decimal("-0.03999999996"))

from math115utils import mark_down
class TestMarkDown(TestMathUtils):

    def test_mark_down_positive_value_by_positive_percentage(self):
        self.assertEqual(mark_down(10, 80), 72)
        self.assertEqual(mark_down("0.0000001", "0.04"), Decimal("0.03999999996"))

    def test_mark_down_positive_value_by_negative_percentage(self):
        self.assertEqual(mark_down(-10, 80), 88)
        self.assertEqual(mark_down("-0.0000001", "0.04"), Decimal("0.04000000004"))

    def test_mark_down_by_zero(self):
        self.assertEqual(mark_down(0, 999), 999)
        self.assertEqual(mark_down(0, -999), -999)
        self.assertEqual(mark_down(0, "0.000001"), Decimal("0.000001"))

    def test_mark_down_negative_value_by_positive_percentage(self):
        self.assertEqual(mark_down(10, -80), -72)
        self.assertEqual(mark_down("0.0000001", "-0.04"), Decimal("-0.03999999996"))
    
    def test_mark_down_negative_value_by_negative_percentage(self):
        self.assertEqual(mark_down(-10, -80), -88)
        self.assertEqual(mark_down("-0.0000001", "-0.04"), Decimal("-0.04000000004"))

from math115utils import closed_interval_overlap
class TestClosedIntervalOverlap(TestMathUtils):

    def test_closed_interval_overlap_for_overlapping_intervals(self):
        self.assertTrue(closed_interval_overlap(1,10, 5,15))
        self.assertTrue(closed_interval_overlap(-20,20, -5,105))
        self.assertTrue(closed_interval_overlap(-120,-20, -25,-5))
        self.assertTrue(closed_interval_overlap(10,15, 1,10))
        self.assertTrue(closed_interval_overlap(-120,-20, -20,-20))

    def test_closed_interval_overlap_for_non_overlapping_intervals(self):
        self.assertFalse(closed_interval_overlap(1,10, 11,15))
        self.assertFalse(closed_interval_overlap(-20,20, -105,-21))
        self.assertFalse(closed_interval_overlap(-120,-20, -19,-5))
        self.assertFalse(closed_interval_overlap(10,15, 1,5))
        self.assertFalse(closed_interval_overlap(-120,-20, -2,-1))

from math115utils import int_to_roman
class TestIntToRoman(TestMathUtils):

    def setUp(self):
        self.known_values = ( (1, 'I'),
                    (2, 'II'),
                    (3, 'III'),
                    (4, 'IV'),
                    (5, 'V'),
                    (6, 'VI'),
                    (7, 'VII'),
                    (8, 'VIII'),
                    (9, 'IX'),
                    (10, 'X'),
                    (50, 'L'),
                    (100, 'C'),
                    (500, 'D'),
                    (1000, 'M'),
                    (31, 'XXXI'),
                    (148, 'CXLVIII'),
                    (294, 'CCXCIV'),
                    (312, 'CCCXII'),
                    (421, 'CDXXI'),
                    (528, 'DXXVIII'),
                    (621, 'DCXXI'),
                    (782, 'DCCLXXXII'),
                    (870, 'DCCCLXX'),
                    (941, 'CMXLI'),
                    (1043, 'MXLIII'),
                    (1110, 'MCX'),
                    (1226, 'MCCXXVI'),
                    (1301, 'MCCCI'),
                    (1485, 'MCDLXXXV'),
                    (1509, 'MDIX'),
                    (1607, 'MDCVII'),
                    (1754, 'MDCCLIV'),
                    (1832, 'MDCCCXXXII'),
                    (1993, 'MCMXCIII'),
                    (2074, 'MMLXXIV'),
                    (2152, 'MMCLII'),
                    (2212, 'MMCCXII'),
                    (2343, 'MMCCCXLIII'),
                    (2499, 'MMCDXCIX'),
                    (2574, 'MMDLXXIV'),
                    (2646, 'MMDCXLVI'),
                    (2723, 'MMDCCXXIII'),
                    (2892, 'MMDCCCXCII'),
                    (2975, 'MMCMLXXV'),
                    (3051, 'MMMLI'),
                    (3185, 'MMMCLXXXV'),
                    (3250, 'MMMCCL'),
                    (3313, 'MMMCCCXIII'),
                    (3408, 'MMMCDVIII'),
                    (3501, 'MMMDI'),
                    (3610, 'MMMDCX'),
                    (3743, 'MMMDCCXLIII'),
                    (3844, 'MMMDCCCXLIV'),
                    (3888, 'MMMDCCCLXXXVIII'),
                    (3940, 'MMMCMXL'),
                    (3999, 'MMMCMXCIX'))

    def test_int_to_roman_for_known_values(self):
        for integer, roman in self.known_values:
            result = int_to_roman(integer)
            self.assertEqual(roman, result)

    def test_int_to_roman_with_bad_input(self):
        with self.assertRaises(TypeError):
            int_to_roman(0.2)
        with self.assertRaises(OutOfRangeError):
            int_to_roman(0)
            int_to_roman(4001)

from math115utils import float_or_zero
class TestFloatOrZero(TestMathUtils):

    def test_float_or_zero_with_float(self):
        self.assertEqual(float_or_zero(1.006), "1.01")
        self.assertEqual(float_or_zero(1.004), "1.00")
        self.assertEqual(float_or_zero(-1.0051), "-1.01")

    def test_float_or_zero_with_string(self):
        self.assertEqual(float_or_zero("1.006"), "1.01")
        self.assertEqual(float_or_zero("1.004"), "1.00")
        self.assertEqual(float_or_zero("-1.0051"), "-1.01")

    def test_float_or_zero_with_euro_string(self):
        self.assertEqual(float_or_zero("1,006"), "1.01")
        self.assertEqual(float_or_zero("1,004"), "1.00")
        self.assertEqual(float_or_zero("-1,0051"), "-1.01")
