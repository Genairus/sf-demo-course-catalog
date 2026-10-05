"""Tests for course unlocking: unlocked_by function."""

import unittest

from catalog import unlocked_by
from catalog.codes import InvalidCourseCode
from tests.fixtures import sample_catalog


class UnlockedByTests(unittest.TestCase):
    # Required tests from acceptance criteria (AC-1 through AC-5)

    def test_single_course_unlocked(self) -> None:
        """C949 unlocks C950 (single dependent course)."""
        catalog = sample_catalog()
        # C950 has C949 as prerequisite
        result = unlocked_by("C949", catalog)
        self.assertEqual(result, ["C950"])

    def test_course_with_multiple_prereqs_d335(self) -> None:
        """D335 is a prerequisite for D287."""
        catalog = sample_catalog()
        # D287 requires D335 and D197
        result = unlocked_by("D335", catalog)
        self.assertEqual(result, ["D287"])

    def test_course_with_multiple_prereqs_d197(self) -> None:
        """D197 is a prerequisite for D287."""
        catalog = sample_catalog()
        # D287 requires D335 and D197
        result = unlocked_by("D197", catalog)
        self.assertEqual(result, ["D287"])

    def test_no_dependents(self) -> None:
        """C950 has no dependents (no course requires it as prerequisite)."""
        catalog = sample_catalog()
        result = unlocked_by("C950", catalog)
        self.assertEqual(result, [])

    def test_code_normalization_lowercase(self) -> None:
        """Lowercase code is normalized to uppercase."""
        catalog = sample_catalog()
        # 'c949' should be normalized to 'C949'
        result = unlocked_by("c949", catalog)
        self.assertEqual(result, ["C950"])

    def test_code_normalization_whitespace(self) -> None:
        """Whitespace in code is stripped during normalization."""
        catalog = sample_catalog()
        # ' c949 ' should be normalized to 'C949'
        result = unlocked_by(" c949 ", catalog)
        self.assertEqual(result, ["C950"])

    def test_unknown_code_raises_valueerror(self) -> None:
        """Unknown course code raises ValueError with code name."""
        catalog = sample_catalog()
        with self.assertRaises(ValueError) as context:
            unlocked_by("Z999", catalog)
        self.assertIn("Z999", str(context.exception))
        self.assertIn("not found", str(context.exception).lower())

    def test_malformed_code_raises_invalidcoursecode(self) -> None:
        """Malformed course code raises InvalidCourseCode."""
        catalog = sample_catalog()
        with self.assertRaises(InvalidCourseCode):
            unlocked_by("not-a-code", catalog)

    def test_sorted_output(self) -> None:
        """Results are returned in sorted order."""
        catalog = sample_catalog()
        # Test with a course that has dependents
        result = unlocked_by("D335", catalog)
        self.assertEqual(result, sorted(result))

    # Additional comprehensive tests

    def test_multiple_dependents_sorted(self) -> None:
        """If multiple courses depend on one, results are sorted."""
        catalog = sample_catalog()
        # Create a hypothetical scenario: if we had a course with multiple dependents
        # In our sample_catalog, D335 and D197 both unlock D287
        # Let's verify sorting is applied
        result = unlocked_by("D197", catalog)
        self.assertEqual(result, sorted(result))

    def test_empty_result_is_sorted_list(self) -> None:
        """Empty result is still a valid sorted list."""
        catalog = sample_catalog()
        result = unlocked_by("C950", catalog)
        self.assertEqual(result, [])
        self.assertEqual(result, sorted(result))

    def test_d333_no_dependents(self) -> None:
        """D333 (Ethics in Technology) has no dependents."""
        catalog = sample_catalog()
        result = unlocked_by("D333", catalog)
        self.assertEqual(result, [])

    def test_result_is_list_of_strings(self) -> None:
        """Result is a list of course code strings."""
        catalog = sample_catalog()
        result = unlocked_by("C949", catalog)
        self.assertIsInstance(result, list)
        for code in result:
            self.assertIsInstance(code, str)

    def test_all_codes_uppercase_in_result(self) -> None:
        """All returned codes are properly normalized (uppercase)."""
        catalog = sample_catalog()
        result = unlocked_by("C949", catalog)
        for code in result:
            self.assertEqual(code, code.upper())

    def test_whitespace_variations(self) -> None:
        """Various whitespace patterns are handled."""
        catalog = sample_catalog()
        # Leading whitespace
        result1 = unlocked_by("  D335", catalog)
        self.assertEqual(result1, ["D287"])
        # Trailing whitespace
        result2 = unlocked_by("D197  ", catalog)
        self.assertEqual(result2, ["D287"])
        # Both
        result3 = unlocked_by("  D197  ", catalog)
        self.assertEqual(result3, ["D287"])

    def test_case_variations(self) -> None:
        """Mixed case codes are normalized correctly."""
        catalog = sample_catalog()
        # All lowercase
        result1 = unlocked_by("c949", catalog)
        self.assertEqual(result1, ["C950"])
        # Mixed case (after upper(), should be valid)
        result2 = unlocked_by("d335", catalog)
        self.assertEqual(result2, ["D287"])


if __name__ == "__main__":
    unittest.main()
