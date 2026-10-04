import unittest

from catalog import Catalog, Course
from catalog.plan import validate_plan
from tests.fixtures import sample_catalog


class ValidatePlanTests(unittest.TestCase):
    def test_empty_plan_is_valid(self) -> None:
        catalog = sample_catalog()
        errors = validate_plan([], catalog)
        self.assertEqual(errors, [])

    def test_single_course_with_no_prerequisites_is_valid(self) -> None:
        catalog = sample_catalog()
        errors = validate_plan([["C949"]], catalog)
        self.assertEqual(errors, [])

    def test_multiple_courses_with_no_prerequisites_is_valid(self) -> None:
        catalog = sample_catalog()
        errors = validate_plan([["C949", "D335", "D197"]], catalog)
        self.assertEqual(errors, [])

    def test_valid_prerequisite_ordering(self) -> None:
        catalog = sample_catalog()
        # C949 must come before C950
        errors = validate_plan([["C949"], ["C950"]], catalog)
        self.assertEqual(errors, [])

    def test_valid_multi_prerequisite_ordering(self) -> None:
        catalog = sample_catalog()
        # D335 and D197 must come before D287
        errors = validate_plan([["D335", "D197"], ["D287"]], catalog)
        self.assertEqual(errors, [])

    def test_malformed_course_code(self) -> None:
        catalog = sample_catalog()
        errors = validate_plan([["not-a-code"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("Malformed course code", errors[0])
        self.assertIn("not-a-code", errors[0])

    def test_unknown_course_code(self) -> None:
        catalog = sample_catalog()
        errors = validate_plan([["Z999"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("Unknown course code", errors[0])
        self.assertIn("Z999", errors[0])

    def test_prerequisite_in_same_term(self) -> None:
        catalog = sample_catalog()
        # C950 requires C949, but both are in term 1
        errors = validate_plan([["C949", "C950"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("C950", errors[0])
        self.assertIn("C949", errors[0])
        self.assertIn("term 1", errors[0])
        self.assertIn("also appears in term 1", errors[0])

    def test_prerequisite_appears_later(self) -> None:
        catalog = sample_catalog()
        # C950 requires C949, but C949 comes later
        errors = validate_plan([["C950"], ["C949"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("C950", errors[0])
        self.assertIn("C949", errors[0])
        self.assertIn("term 1", errors[0])
        self.assertIn("term 2", errors[0])

    def test_prerequisite_missing_from_plan(self) -> None:
        catalog = sample_catalog()
        # C950 requires C949, but C949 is not in the plan
        errors = validate_plan([["C950"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("C950", errors[0])
        self.assertIn("C949", errors[0])
        self.assertIn("not in the plan", errors[0])

    def test_multiple_missing_prerequisites(self) -> None:
        catalog = sample_catalog()
        # D287 requires D335 and D197, but neither is in the plan
        errors = validate_plan([["D287"]], catalog)
        self.assertEqual(len(errors), 2)
        # Should report both missing prerequisites
        all_errors = " ".join(errors)
        self.assertIn("D335", all_errors)
        self.assertIn("D197", all_errors)

    def test_multiple_errors_in_plan(self) -> None:
        catalog = sample_catalog()
        # Multiple issues: unknown code, malformed code, missing prerequisite
        errors = validate_plan([["Z999", "not-a-code", "C950"]], catalog)
        self.assertEqual(len(errors), 3)

    def test_case_insensitive_course_codes(self) -> None:
        catalog = sample_catalog()
        # Lowercase codes should be normalized
        errors = validate_plan([["c949"], ["c950"]], catalog)
        self.assertEqual(errors, [])

    def test_prerequisite_satisfied_in_earlier_term(self) -> None:
        catalog = sample_catalog()
        # C949 in term 1, C950 in term 3 should be valid
        errors = validate_plan([["C949"], ["D335"], ["C950"]], catalog)
        self.assertEqual(errors, [])

    def test_complex_valid_plan(self) -> None:
        catalog = sample_catalog()
        plan = [
            ["C949", "D335", "D197"],  # Term 1: courses with no prerequisites
            ["C950", "D333"],  # Term 2: C950 requires C949 (satisfied)
            ["D287"],  # Term 3: D287 requires D335 and D197 (both satisfied)
        ]
        errors = validate_plan(plan, catalog)
        self.assertEqual(errors, [])

    def test_complex_invalid_plan(self) -> None:
        catalog = sample_catalog()
        plan = [
            ["C950", "D287"],  # Term 1: both have unsatisfied prerequisites
            ["C949"],  # Term 2: C949 is a prerequisite that comes too late
        ]
        errors = validate_plan(plan, catalog)
        # C950 requires C949 (appears later), D287 requires D335 and D197 (missing)
        self.assertGreaterEqual(len(errors), 3)

    def test_empty_term_in_plan(self) -> None:
        catalog = sample_catalog()
        errors = validate_plan([["C949"], [], ["C950"]], catalog)
        self.assertEqual(errors, [])

    def test_malformed_code_does_not_break_validation(self) -> None:
        catalog = sample_catalog()
        # Malformed code should be reported but not break rest of validation
        errors = validate_plan([["C949", "bad-code"], ["C950"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("Malformed course code", errors[0])


if __name__ == "__main__":
    unittest.main()
