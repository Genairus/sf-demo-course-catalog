import unittest

from catalog import Catalog, Course
from catalog.cycles import find_prerequisite_cycles


class FindPrerequisiteCyclesTests(unittest.TestCase):
    """Test suite for prerequisite cycle detection."""

    def test_no_cycles(self) -> None:
        """AC-1, AC-5: Catalog with no cycles returns empty list."""
        catalog = Catalog([
            Course("C949", "Data Structures I", 4),
            Course("C950", "Data Structures II", 4, prerequisites=("C949",)),
            Course("D335", "Python Programming", 3),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(cycles, [])

    def test_two_course_cycle(self) -> None:
        """AC-1, AC-3, AC-5: Two-course cycle A->B->A is detected."""
        catalog = Catalog([
            Course("C949", "Course A", 4, prerequisites=("C950",)),
            Course("C950", "Course B", 4, prerequisites=("C949",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        # Cycle should be normalized to start with lex-smallest code
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0], ["C949", "C950"])

    def test_three_course_cycle(self) -> None:
        """AC-1, AC-3, AC-5: Three-course cycle A->B->C->A is detected."""
        # Create cycle: C100 requires C300, C300 requires C200, C200 requires C100
        # Path: C100 -> C300 -> C200 -> C100 (following prerequisite edges)
        catalog = Catalog([
            Course("C100", "Course A", 3, prerequisites=("C300",)),
            Course("C200", "Course B", 3, prerequisites=("C100",)),
            Course("C300", "Course C", 3, prerequisites=("C200",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        # Cycle should be normalized to start with lex-smallest code (C100)
        # The cycle follows the prerequisite chain: C100 -> C300 -> C200 -> back to C100
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0], ["C100", "C300", "C200"])

    def test_self_prerequisite(self) -> None:
        """AC-2, AC-5: Self-prerequisite A->A is detected as [[A]]."""
        catalog = Catalog([
            Course("C949", "Self-referential course", 4, prerequisites=("C949",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0], ["C949"])

    def test_unknown_prerequisite_ignored(self) -> None:
        """AC-4, AC-5: Unknown prerequisite is ignored (no cycle reported)."""
        catalog = Catalog([
            Course("C950", "Course with unknown prerequisite", 4, prerequisites=("Z999",)),
        ])
        cycles = find_prerequisite_cycles(catalog)
        # Z999 doesn't exist in catalog, so it's ignored (treated as having no outgoing edges)
        self.assertEqual(cycles, [])


if __name__ == "__main__":
    unittest.main()
