"""Tests for progress tracking: available_courses function."""

import unittest

from catalog import available_courses
from catalog.codes import InvalidCourseCode
from tests.fixtures import sample_catalog


class AvailableCoursesTests(unittest.TestCase):
    # Required tests from acceptance criteria (AC-4)

    def test_nothing_completed(self) -> None:
        """Only courses without prerequisites are available when nothing is completed."""
        catalog = sample_catalog()
        # Courses with no prerequisites: C949, D335, D197, D333
        # Courses with prerequisites: C950 (needs C949), D287 (needs D335, D197)
        available = available_courses([], catalog)
        self.assertIn("C949", available)
        self.assertIn("D335", available)
        self.assertIn("D197", available)
        self.assertIn("D333", available)
        self.assertNotIn("C950", available)
        self.assertNotIn("D287", available)

    def test_partially_satisfied_prerequisite(self) -> None:
        """Course with incomplete prerequisites is not available."""
        catalog = sample_catalog()
        # D287 requires both D335 and D197 - only complete D335
        available = available_courses(["D335"], catalog)
        self.assertIn("C949", available)
        self.assertIn("D197", available)
        self.assertIn("D333", available)
        # D287 should NOT be available - D197 not completed
        self.assertNotIn("D287", available)

    def test_course_becomes_available(self) -> None:
        """Course becomes available once all prerequisites are completed."""
        catalog = sample_catalog()
        # Complete C949, C950 should become available
        available = available_courses(["C949"], catalog)
        self.assertIn("C950", available)  # Prereq C949 satisfied
        self.assertIn("D335", available)
        self.assertIn("D197", available)
        self.assertIn("D333", available)
        # C949 already completed, so not in available
        self.assertNotIn("C949", available)
        # D287 needs D335 and D197 - not yet completed
        self.assertNotIn("D287", available)

    def test_completed_courses_excluded(self) -> None:
        """Completed courses are not in results."""
        catalog = sample_catalog()
        # Complete several courses
        available = available_courses(["C949", "C950", "D333"], catalog)
        # None of the completed courses should be in available
        self.assertNotIn("C949", available)
        self.assertNotIn("C950", available)
        self.assertNotIn("D333", available)
        # But other courses should be
        self.assertIn("D335", available)
        self.assertIn("D197", available)

    def test_code_normalization(self) -> None:
        """Lowercase and whitespace in codes work correctly."""
        catalog = sample_catalog()
        # Codes should be normalized: lowercase -> uppercase, whitespace stripped
        available = available_courses([" c949 ", "d335", " D197 "], catalog)
        # C950 should be available (C949 completed)
        self.assertIn("C950", available)
        # D287 should be available (D335 and D197 completed)
        self.assertIn("D287", available)
        # Completed courses excluded
        self.assertNotIn("C949", available)
        self.assertNotIn("D335", available)
        self.assertNotIn("D197", available)

    def test_unknown_code_raises_valueerror(self) -> None:
        """Unknown code raises ValueError with code name."""
        catalog = sample_catalog()
        with self.assertRaises(ValueError) as context:
            available_courses(["Z999"], catalog)
        self.assertIn("Z999", str(context.exception))
        self.assertIn("not found", str(context.exception).lower())

    # Additional comprehensive tests

    def test_malformed_code_raises_valueerror(self) -> None:
        """Malformed code raises InvalidCourseCode."""
        catalog = sample_catalog()
        with self.assertRaises(InvalidCourseCode):
            available_courses(["not-a-code"], catalog)

    def test_empty_completed_list(self) -> None:
        """Empty completed list returns only courses without prerequisites."""
        catalog = sample_catalog()
        available = available_courses([], catalog)
        # Same as test_nothing_completed
        self.assertEqual(sorted(["C949", "D335", "D197", "D333"]), available)

    def test_all_courses_available(self) -> None:
        """All courses available when all prerequisites are completed."""
        catalog = sample_catalog()
        # Complete prerequisite courses only
        available = available_courses(["C949", "D335", "D197"], catalog)
        # Remaining courses: C950 (prereq satisfied), D333 (no prereq), D287 (prereqs satisfied)
        self.assertIn("C950", available)
        self.assertIn("D333", available)
        self.assertIn("D287", available)

    def test_sorting_verification(self) -> None:
        """Results are returned in sorted order."""
        catalog = sample_catalog()
        available = available_courses([], catalog)
        self.assertEqual(available, sorted(available))
        # Also verify specific sorting
        self.assertEqual(available, ["C949", "D197", "D333", "D335"])

    def test_single_course_completed(self) -> None:
        """Single course completed is excluded from available."""
        catalog = sample_catalog()
        available = available_courses(["C949"], catalog)
        # C950 now has its prerequisite satisfied
        self.assertIn("C950", available)
        self.assertNotIn("C949", available)

    def test_completed_courses_do_not_affect_other_prereqs(self) -> None:
        """Completing one course doesn't make unrelated prerequisite courses available."""
        catalog = sample_catalog()
        # Complete only C949
        available = available_courses(["C949"], catalog)
        # D287 should NOT be available (needs D335 and D197)
        self.assertNotIn("D287", available)
        # C950 should be available (needs only C949)
        self.assertIn("C950", available)

    def test_all_prereqs_completed_allows_dependent(self) -> None:
        """When all prerequisites of a course are completed, it becomes available."""
        catalog = sample_catalog()
        # Complete all prerequisites for D287
        available = available_courses(["D335", "D197"], catalog)
        self.assertIn("D287", available)

    def test_unknown_code_in_mixed_list_raises_first(self) -> None:
        """Unknown code raises ValueError even when mixed with valid codes."""
        catalog = sample_catalog()
        # Should raise on unknown code
        with self.assertRaises(ValueError) as context:
            available_courses(["C949", "Z999", "D335"], catalog)
        self.assertIn("Z999", str(context.exception))

    def test_malformed_code_in_mixed_list_raises_first(self) -> None:
        """Malformed code raises InvalidCourseCode even when mixed with valid codes."""
        catalog = sample_catalog()
        # Should raise on malformed code
        with self.assertRaises(InvalidCourseCode):
            available_courses(["C949", "bad", "D335"], catalog)


if __name__ == "__main__":
    unittest.main()
