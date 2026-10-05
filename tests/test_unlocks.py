import unittest

from catalog import unlocked_by
from tests.fixtures import sample_catalog


class UnlockedByTests(unittest.TestCase):
    def test_c949_unlocks_c950(self) -> None:
        """AC-1: C949 unlocks C950."""
        catalog = sample_catalog()
        result = unlocked_by("C949", catalog)
        self.assertEqual(result, ["C950"])

    def test_d335_unlocks_d287(self) -> None:
        """AC-1: D335 unlocks D287."""
        catalog = sample_catalog()
        result = unlocked_by("D335", catalog)
        self.assertEqual(result, ["D287"])

    def test_case_insensitive(self) -> None:
        """AC-2: Case insensitive lookup."""
        catalog = sample_catalog()
        result = unlocked_by("c949", catalog)
        self.assertEqual(result, ["C950"])

    def test_unknown_code_raises_value_error(self) -> None:
        """AC-3: Unknown code raises ValueError."""
        catalog = sample_catalog()
        with self.assertRaises(ValueError) as ctx:
            unlocked_by("Z999", catalog)
        self.assertIn("not found", str(ctx.exception))

    def test_malformed_code_raises_invalid_course_code(self) -> None:
        """AC-3: Malformed code raises InvalidCourseCode."""
        catalog = sample_catalog()
        from catalog import InvalidCourseCode
        with self.assertRaises(InvalidCourseCode):
            unlocked_by("not-a-code", catalog)

    def test_no_prerequisites_returns_empty_list(self) -> None:
        """AC-4: Course with no prerequisites for it returns empty list."""
        catalog = sample_catalog()
        result = unlocked_by("C950", catalog)
        self.assertEqual(result, [])

    def test_d197_unlocks_d287(self) -> None:
        """Additional: D197 also unlocks D287."""
        catalog = sample_catalog()
        result = unlocked_by("D197", catalog)
        self.assertEqual(result, ["D287"])

    def test_result_is_sorted(self) -> None:
        """AC-5: Result is sorted."""
        catalog = sample_catalog()
        result = unlocked_by("D335", catalog)
        self.assertEqual(result, sorted(result))


if __name__ == "__main__":
    unittest.main()
