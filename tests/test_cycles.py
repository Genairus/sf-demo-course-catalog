"""Tests for prerequisite cycle detection."""

import unittest

from catalog import Catalog, Course
from catalog.cycles import find_prerequisite_cycles
from tests.fixtures import sample_catalog


class FindPrerequisiteCyclesTests(unittest.TestCase):
    """Tests for find_prerequisite_cycles covering all cycle scenarios."""

    def test_no_cycles_returns_empty_list(self) -> None:
        """AC-5: A catalog with no cycles returns an empty list."""
        catalog = sample_catalog()
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_two_course_cycle(self) -> None:
        """Two-course cycle A->B->A is detected."""
        catalog = Catalog([
            Course("C101", "Intro", 3, prerequisites=("C102",)),
            Course("C102", "Advanced", 3, prerequisites=("C101",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        # Cycle should be reported once, normalized to start with smallest code
        self.assertEqual(len(cycles), 1)
        cycle = cycles[0]
        self.assertEqual(cycle[0], "C101")  # Start with lexicographically smallest
        self.assertIn("C102", cycle)
        self.assertEqual(cycle[0], cycle[-1])  # Should start and end with same course

    def test_three_course_cycle(self) -> None:
        """Three-course cycle A->B->C->A is detected."""
        catalog = Catalog([
            Course("C101", "Course A", 3, prerequisites=("C102",)),
            Course("C102", "Course B", 3, prerequisites=("C103",)),
            Course("C103", "Course C", 3, prerequisites=("C101",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 1)
        cycle = cycles[0]
        # Normalized to start with C101
        self.assertEqual(cycle[0], "C101")
        self.assertIn("C102", cycle)
        self.assertIn("C103", cycle)
        self.assertEqual(cycle[0], cycle[-1])

    def test_self_prerequisite(self) -> None:
        """Self-prerequisite A->A creates a cycle of length 1."""
        catalog = Catalog([
            Course("C101", "Self-Referential", 3, prerequisites=("C101",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 1)
        cycle = cycles[0]
        # Self-prerequisite should be detected
        self.assertEqual(cycle, ("C101", "C101"))

    def test_unknown_prerequisite_ignored_not_a_cycle(self) -> None:
        """Unknown prerequisite is ignored, does not create a cycle."""
        catalog = Catalog([
            Course("C101", "Intro", 3, prerequisites=("C999",)),  # C999 doesn't exist
        ])
        cycles = find_prerequisite_cycles(catalog)
        # Unknown prerequisite should not cause a cycle
        self.assertEqual(cycles, [])

    def test_cycle_reported_only_once(self) -> None:
        """Cycles are not duplicated in the result."""
        catalog = Catalog([
            Course("C101", "A", 3, prerequisites=("C102",)),
            Course("C102", "B", 3, prerequisites=("C101",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        # Even though DFS might traverse multiple times, cycle should appear once
        self.assertEqual(len(cycles), 1)

    def test_multiple_independent_cycles(self) -> None:
        """Multiple independent cycles are all detected."""
        catalog = Catalog([
            # First cycle: C101 <-> C102
            Course("C101", "A", 3, prerequisites=("C102",)),
            Course("C102", "B", 3, prerequisites=("C101",)),
            # Second cycle: C201 <-> C202
            Course("C201", "C", 3, prerequisites=("C202",)),
            Course("C202", "D", 3, prerequisites=("C201",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 2)

    def test_empty_catalog_returns_empty_list(self) -> None:
        """Empty catalog has no cycles."""
        catalog = Catalog([])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_courses_with_no_prerequisites_no_cycles(self) -> None:
        """Courses with no prerequisites cannot form cycles."""
        catalog = Catalog([
            Course("C101", "Intro", 3),
            Course("C102", "Advanced", 3),
            Course("C103", "Expert", 3),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_linear_prerequisite_chain_no_cycles(self) -> None:
        """Linear prerequisite chain does not form a cycle."""
        catalog = Catalog([
            Course("C101", "Intro", 3),
            Course("C102", "Intermediate", 3, prerequisites=("C101",)),
            Course("C103", "Advanced", 3, prerequisites=("C102",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_diamond_dependency_no_cycle(self) -> None:
        """Diamond-shaped dependency graph with no back edge has no cycle."""
        catalog = Catalog([
            Course("C101", "Base", 3),
            Course("C102", "Left", 3, prerequisites=("C101",)),
            Course("C103", "Right", 3, prerequisites=("C101",)),
            Course("C104", "Top", 3, prerequisites=("C102", "C103")),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])


if __name__ == "__main__":
    unittest.main()
