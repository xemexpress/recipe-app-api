from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):
    """Test the calc module."""

    def test_sum(self):
        """Test adding numbers together."""
        x = 1
        y = 10

        res = calc.add(x, y)

        self.assertEqual(res, 11)

    def test_subtract(self):
        """Test subtracting numbers together."""
        x = 11
        y = 1

        res = calc.subtract(x, y)

        self.assertEqual(res, 10)
