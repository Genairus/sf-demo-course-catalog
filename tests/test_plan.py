"""Tests for catalog.plan.validate_plan()."""

import unittest

from catalog.plan import validate_plan
from tests.fixtures import sample_catalog


class ValidatePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = sample_catalog()

    # ------------------------------------------------------------------
    # Happy path – a fully valid plan produces no problems
    # ------------------------------------------------------------------
    def test_valid_plan_has_no_problems(self) -> None:
        # C949 before C950; D335 and D197 before D287 (matches notes_for_coder)
        terms = [
            ["C949", "D335", "D197"],
            ["C950", "D287"],
        ]
        self.assertEqual(validate_plan(terms, self.catalog), [])

    def test_empty_plan_has_no_problems(self) -> None:
        self.assertEqual(validate_plan([], self.catalog), [])

    # ------------------------------------------------------------------
    # AC-4 – malformed course codes
    # ------------------------------------------------------------------
    def test_malformed_code_is_reported(self) -> None:
        terms = [["not-a-code"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("not-a-code", problems[0])
        self.assertIn("Malformed", problems[0])

    def test_multiple_malformed_codes_reported_separately(self) -> None:
        terms = [["bad-code", "123"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 2)

    # ------------------------------------------------------------------
    # AC-4 – valid-format but unknown codes
    # ------------------------------------------------------------------
    def test_unknown_code_is_reported(self) -> None:
        terms = [["Z999"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("Z999", problems[0])
        self.assertIn("Unknown", problems[0])

    def test_multiple_unknown_codes_reported_separately(self) -> None:
        terms = [["Z999", "A001"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 2)

    # ------------------------------------------------------------------
    # AC-3 – prerequisite missing from the plan entirely
    # ------------------------------------------------------------------
    def test_missing_prerequisite_is_reported(self) -> None:
        # D287 requires D335 and D197; neither is in the plan
        terms = [["D287"]]
        problems = validate_plan(terms, self.catalog)
        # Both D335 and D197 are missing
        codes_mentioned = " ".join(problems)
        self.assertIn("D335", codes_mentioned)
        self.assertIn("D197", codes_mentioned)

    def test_single_missing_prerequisite(self) -> None:
        # C950 requires C949, which is absent
        terms = [["C950"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("C949", problems[0])
        self.assertIn("not in the plan", problems[0])

    # ------------------------------------------------------------------
    # AC-2 – prerequisite in the same or a later term
    # ------------------------------------------------------------------
    def test_prerequisite_in_same_term_is_reported(self) -> None:
        # C950 requires C949; both in term 1
        terms = [["C949", "C950"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("C950", problems[0])
        self.assertIn("C949", problems[0])
        self.assertIn("same or a later term", problems[0])

    def test_prerequisite_in_later_term_is_reported(self) -> None:
        # C950 in term 1, C949 in term 2
        terms = [["C950"], ["C949"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("C950", problems[0])
        self.assertIn("C949", problems[0])

    def test_term_numbers_are_correct_in_messages(self) -> None:
        # C950 in term 2, C949 in term 3 → C949 is in a later term (3)
        terms = [[], ["C950"], ["C949"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("term 2", problems[0])   # course term
        self.assertIn("term 3", problems[0])   # prereq term

    def test_prerequisite_in_strictly_earlier_term_is_ok(self) -> None:
        terms = [["C949"], ["C950"]]
        self.assertEqual(validate_plan(terms, self.catalog), [])

    # ------------------------------------------------------------------
    # Edge cases and combinations
    # ------------------------------------------------------------------
    def test_no_problems_raised_only_returned(self) -> None:
        """validate_plan must never raise; problems are returned."""
        terms = [["not-a-code", "Z999", "C950"]]
        # If validate_plan raises an exception, the test will fail.
        problems = validate_plan(terms, self.catalog)
        self.assertGreater(len(problems), 0)

    def test_lowercase_codes_accepted(self) -> None:
        # lowercase is valid format; c950 is known
        terms = [["c949"], ["c950"]]
        self.assertEqual(validate_plan(terms, self.catalog), [])

    def test_malformed_code_not_counted_as_missing_prerequisite(self) -> None:
        # A malformed code should produce only one error (Malformed), not a cascade
        terms = [["not-a-code"]]
        problems = validate_plan(terms, self.catalog)
        self.assertEqual(len(problems), 1)
        self.assertIn("Malformed", problems[0])


if __name__ == "__main__":
    unittest.main()
