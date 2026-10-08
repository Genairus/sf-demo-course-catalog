"""Tests for cycle detection in prerequisite dependencies."""

import unittest

from catalog import Catalog, find_prerequisite_cycles
from catalog.models import Course


class PrerequisiteCycleTests(unittest.TestCase):
    """Test cases for find_prerequisite_cycles according to AC-5 acceptance criteria."""

    def test_no_cycles(self) -> None:
        """AC-5: Catalog with no prerequisites and simple prerequisites returns []."""
        catalog = Catalog(
            [
                Course("A101", "Course A", 3),
                Course("B202", "Course B", 3),
                Course("C303", "Course C", 3, prerequisites=("A101",)),
            ]
        )
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_two_course_cycle(self) -> None:
        """AC-5: C950 -> C949 -> C950 returns [['C949', 'C950', 'C949']]."""
        catalog = Catalog(
            [
                Course("C949", "Data Structures I", 4, prerequisites=("C950",)),
                Course("C950", "Data Structures II", 4, prerequisites=("C949",)),
            ]
        )
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 1)
        # Cycle should start with lexicographically smallest, and end where it starts
        self.assertEqual(cycles[0], ["C949", "C950", "C949"])

    def test_three_course_cycle(self) -> None:
        """AC-5: A101 -> C949 -> B202 -> A101 returns [['A101', 'C949', 'B202', 'A101']]."""
        catalog = Catalog(
            [
                Course("A101", "Course A", 3, prerequisites=("C949",)),
                Course("B202", "Course B", 3, prerequisites=("A101",)),
                Course("C949", "Course C", 3, prerequisites=("B202",)),
            ]
        )
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 1)
        # Cycle: A101->C949->B202->A101
        # DFS from A101 gives path [A101, C949, B202], cycle starts at A101
        # Normalized to start with lexicographically smallest: [A101, C949, B202]
        # With trailing start element: [A101, C949, B202, A101]
        self.assertEqual(cycles[0], ["A101", "C949", "B202", "A101"])

    def test_self_prerequisite(self) -> None:
        """AC-5: Course with itself as prerequisite returns [['C949', 'C949']]."""
        catalog = Catalog(
            [
                Course("C949", "Data Structures I", 4, prerequisites=("C949",)),
            ]
        )
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 1)
        # Self-loop cycle: starts and ends with same course
        self.assertEqual(cycles[0], ["C949", "C949"])

    def test_unknown_prerequisite_ignored(self) -> None:
        """AC-5: Prerequisite not in catalog is silently ignored."""
        catalog = Catalog(
            [
                Course("C949", "Data Structures I", 4, prerequisites=("Z999",)),
            ]
        )
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_cycle_reported_once(self) -> None:
        """AC-5: Cycles are deduplicated (canonically normalized)."""
        catalog = Catalog(
            [
                # Create a cycle A101 -> C303 -> B202 -> A101
                Course("A101", "Course A", 3, prerequisites=("C303",)),
                Course("B202", "Course B", 3, prerequisites=("A101",)),
                Course("C303", "Course C", 3, prerequisites=("B202",)),
            ]
        )
        cycles = find_prerequisite_cycles(catalog)
        # Should be exactly one cycle, deduplicated from all starting points
        self.assertEqual(len(cycles), 1)
        # Cycle: A101->C303->B202->A101
        # DFS from A101 gives path [A101, C303, B202], cycle starts at A101
        # Normalized to start with lexicographically smallest: [A101, C303, B202]
        # With trailing start element: [A101, C303, B202, A101]
        self.assertEqual(cycles[0], ["A101", "C303", "B202", "A101"])


if __name__ == "__main__":
    unittest.main()
