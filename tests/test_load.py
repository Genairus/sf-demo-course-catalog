"""Tests for catalog.load.check_term_loads()."""

import unittest

from catalog import Catalog
from catalog.load import check_term_loads
from tests.fixtures import sample_catalog


class CheckTermLoadsTests(unittest.TestCase):
    # ------------------------------------------------------------------ #
    # Basic validation                                                     #
    # ------------------------------------------------------------------ #

    def test_non_positive_max_units_raises(self) -> None:
        """AC-1: ValueError when max_units <= 0."""
        catalog = sample_catalog()
        with self.assertRaises(ValueError) as ctx:
            check_term_loads([], catalog, max_units=0)
        self.assertEqual(str(ctx.exception), "max_units must be positive")

    def test_negative_max_units_raises(self) -> None:
        """AC-1: Negative max_units is also rejected."""
        catalog = sample_catalog()
        with self.assertRaises(ValueError) as ctx:
            check_term_loads([], catalog, max_units=-5)
        self.assertEqual(str(ctx.exception), "max_units must be positive")

    # ------------------------------------------------------------------ #
    # Empty / trivially-valid inputs                                       #
    # ------------------------------------------------------------------ #

    def test_empty_plan_returns_empty_list(self) -> None:
        """AC-2: No terms → no errors."""
        errors = check_term_loads([], Catalog())
        self.assertEqual(errors, [])

    def test_empty_term_returns_empty_list(self) -> None:
        """AC-2: An empty term has zero CUs, which never exceeds any positive limit."""
        errors = check_term_loads([[]], sample_catalog())
        self.assertEqual(errors, [])

    def test_term_within_limit_returns_empty_list(self) -> None:
        """AC-2: Term whose total ≤ max_units produces no error."""
        catalog = sample_catalog()
        # C949=4 CU, D197=1 CU → total 5 CU, limit 12
        errors = check_term_loads([["C949", "D197"]], catalog)
        self.assertEqual(errors, [])

    # ------------------------------------------------------------------ #
    # Exceeding the limit                                                  #
    # ------------------------------------------------------------------ #

    def test_term_exceeding_limit_reports_error(self) -> None:
        """AC-1/AC-2: Term that exceeds max_units is reported."""
        catalog = sample_catalog()
        # C949=4 + C950=4 + D335=3 + D197=1 = 12 CU; limit 11 → one error
        errors = check_term_loads([["C949", "C950", "D335", "D197"]], catalog, max_units=11)
        self.assertEqual(len(errors), 1)
        self.assertIn("Term 1", errors[0])
        self.assertIn("12 CU", errors[0])
        self.assertIn("limit 11 CU", errors[0])

    def test_error_message_format(self) -> None:
        """AC-3: Error message follows the exact required format."""
        catalog = sample_catalog()
        # C949=4 CU, limit 3
        errors = check_term_loads([["C949"]], catalog, max_units=3)
        self.assertEqual(errors, ["Term 1 exceeds load limit: 4 CU (limit 3 CU)"])

    def test_multiple_terms_only_over_limit_reported(self) -> None:
        """AC-2: Only terms that exceed the limit appear in the result."""
        catalog = sample_catalog()
        # Term 1: C949=4 CU (within limit 5)
        # Term 2: C949=4, D335=3, D197=1 = 8 CU (exceeds limit 5)
        errors = check_term_loads(
            [["C949"], ["C949", "D335", "D197"]],
            catalog,
            max_units=5,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("Term 2", errors[0])

    def test_multiple_over_limit_terms_all_reported(self) -> None:
        """AC-2: Every over-limit term is reported."""
        catalog = sample_catalog()
        # Both terms have C949=4 CU and D335=3 CU → 7 CU, limit 6
        errors = check_term_loads(
            [["C949", "D335"], ["C949", "D335"]],
            catalog,
            max_units=6,
        )
        self.assertEqual(len(errors), 2)
        self.assertIn("Term 1", errors[0])
        self.assertIn("Term 2", errors[1])

    def test_term_numbering_starts_at_1(self) -> None:
        """AC-3: Term numbers in messages are 1-based."""
        catalog = sample_catalog()
        # First term is fine, third term exceeds
        errors = check_term_loads(
            [["D197"], ["D197"], ["C949", "D335", "D197"]],  # 1, 1, 8 CU
            catalog,
            max_units=5,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("Term 3", errors[0])

    # ------------------------------------------------------------------ #
    # Unknown / malformed codes are silently skipped                       #
    # ------------------------------------------------------------------ #

    def test_unknown_codes_silently_skipped(self) -> None:
        """AC-2: Unknown course codes count as zero CU (no crash, no error message for them)."""
        catalog = sample_catalog()
        # Z999 is unknown → 0 CU; within limit
        errors = check_term_loads([["Z999"]], catalog, max_units=1)
        self.assertEqual(errors, [])

    def test_malformed_codes_silently_skipped(self) -> None:
        """AC-2: Malformed codes also count as zero CU."""
        catalog = sample_catalog()
        errors = check_term_loads([["not-a-code"]], catalog, max_units=1)
        self.assertEqual(errors, [])

    # ------------------------------------------------------------------ #
    # Default limit                                                        #
    # ------------------------------------------------------------------ #

    def test_default_max_units_is_12(self) -> None:
        """AC-1: Default limit is 12 CU."""
        catalog = sample_catalog()
        # C949=4 + C950=4 + D335=3 + D197=1 = 12 CU — exactly at the limit, not over
        errors = check_term_loads([["C949", "C950", "D335", "D197"]], catalog)
        self.assertEqual(errors, [])

    def test_default_max_units_exceeded(self) -> None:
        """AC-1: 13 CU with default limit (12) triggers an error."""
        catalog = sample_catalog()
        # C949=4 + C950=4 + D335=3 + D197=1 + D333=3 = 15 CU
        errors = check_term_loads([["C949", "C950", "D335", "D197", "D333"]], catalog)
        self.assertEqual(len(errors), 1)
        self.assertIn("15 CU", errors[0])
        self.assertIn("limit 12 CU", errors[0])


class TestCheckTermLoads(unittest.TestCase):
    """Test cases for check_term_loads per AC-4."""

    def test_term_under_limit(self) -> None:
        """Single term with total < max_units returns []."""
        catalog = sample_catalog()
        # C949=4 CU, D197=1 CU → total 5 CU, limit 12
        errors = check_term_loads([["C949", "D197"]], catalog, max_units=12)
        self.assertEqual(errors, [])

    def test_term_at_limit(self) -> None:
        """Single term with total == max_units returns []."""
        catalog = sample_catalog()
        # C949=4 CU + C950=4 CU = 8 CU, limit 8
        errors = check_term_loads([["C949", "C950"]], catalog, max_units=8)
        self.assertEqual(errors, [])

    def test_term_over_limit(self) -> None:
        """Single term with total > max_units returns one problem string."""
        catalog = sample_catalog()
        # C949=4 CU + C950=4 CU = 8 CU, limit 7 → exceeds by 1
        errors = check_term_loads([["C949", "C950"]], catalog, max_units=7)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], str)
        self.assertIn("Term 1", errors[0])
        self.assertIn("8", errors[0])

    def test_unknown_codes_count_as_zero(self) -> None:
        """Term with only unknown codes returns [] (total=0, not over limit)."""
        catalog = sample_catalog()
        # Z999 is unknown → 0 CU; within limit
        errors = check_term_loads([["Z999"]], catalog, max_units=12)
        self.assertEqual(errors, [])

    def test_invalid_max_units_raises(self) -> None:
        """check_term_loads with max_units <= 0 raises ValueError."""
        catalog = sample_catalog()
        with self.assertRaises(ValueError):
            check_term_loads([], catalog, max_units=0)
        with self.assertRaises(ValueError):
            check_term_loads([], catalog, max_units=-1)

    def test_multiple_terms_flags_only_overloaded(self) -> None:
        """Plan with two terms, one over and one under, returns exactly one problem."""
        catalog = sample_catalog()
        # Term 1: C949=4 CU (within limit 5)
        # Term 2: C949=4, D335=3, D197=1 = 8 CU (exceeds limit 5)
        errors = check_term_loads(
            [["C949"], ["C949", "D335", "D197"]],
            catalog,
            max_units=5,
        )
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], str)
        self.assertIn("Term 2", errors[0])
        self.assertNotIn("Term 1", errors[0])
        self.assertIn("8", errors[0])

    def test_malformed_codes_count_as_zero(self) -> None:
        """Term with malformed codes ('bad-code') counts as 0 CU, no problem."""
        catalog = sample_catalog()
        # Malformed code counts as 0 CU; within default limit
        errors = check_term_loads([["bad-code"]], catalog)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
