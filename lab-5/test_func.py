import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides


class TestGetTriangleType(unittest.TestCase):

    # ========== ПОЗИТИВНЫЕ ТЕСТЫ ==========

    def test_equilateral(self):
        self.assertEqual(get_triangle_type(5, 5, 5), "equilateral")

    def test_equilateral_float(self):
        self.assertEqual(get_triangle_type(2.5, 2.5, 2.5), "equilateral")

    def test_equilateral_small(self):
        self.assertEqual(get_triangle_type(0.1, 0.1, 0.1), "equilateral")

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(6, 6, 7), "isosceles")

    def test_isosceles_float(self):
        self.assertEqual(get_triangle_type(5.5, 5.5, 6.0), "isosceles")

    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")

    def test_nonequilateral_float(self):
        self.assertEqual(get_triangle_type(1.5, 2.0, 2.5), "nonequilateral")

    # ========== НЕГАТИВНЫЕ ТЕСТЫ ==========

    def test_zero_side(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 5, 5)

    def test_negative_side(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-3, 4, 5)

    def test_all_zeros(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 0, 0)

    def test_triangle_inequality_equal(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)

    def test_triangle_inequality_less(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 1, 3)

    def test_invalid_type_string(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type("5", 4, 5)

    def test_invalid_type_none(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(5, None, 5)

    def test_invalid_type_list(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type([1], 2, 3)

    def test_mixed_invalid(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, "a", 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)