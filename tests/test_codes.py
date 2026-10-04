import unittest

from catalog.codes import InvalidCourseCode, is_valid_code, normalize_code


class NormalizeCodeTests(unittest.TestCase):
    def test_uppercases_and_strips(self) -> None:
        self.assertEqual(normalize_code(" d335 "), "D335")

    def test_accepts_three_and_four_digits(self) -> None:
        self.assertEqual(normalize_code("C949"), "C949")
        self.assertEqual(normalize_code("C1928"), "C1928")

    def test_rejects_malformed_codes(self) -> None:
        for raw in ("", "949", "CC949", "C94", "C19285", "C-949"):
            with self.subTest(raw=raw), self.assertRaises(InvalidCourseCode):
                normalize_code(raw)

    def test_is_valid_code(self) -> None:
        self.assertTrue(is_valid_code("c949"))
        self.assertFalse(is_valid_code("nope"))


if __name__ == "__main__":
    unittest.main()
