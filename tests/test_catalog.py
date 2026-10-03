import unittest

from catalog import Catalog, Course
from tests.fixtures import sample_catalog


class CatalogTests(unittest.TestCase):
    def test_lookup_is_case_insensitive(self) -> None:
        catalog = sample_catalog()
        course = catalog.get("c950")
        assert course is not None
        self.assertEqual(course.prerequisites, ("C949",))

    def test_unknown_and_malformed_codes_are_none(self) -> None:
        catalog = sample_catalog()
        self.assertIsNone(catalog.get("Z999"))
        self.assertIsNone(catalog.get("not-a-code"))
        self.assertNotIn("Z999", catalog)

    def test_duplicate_codes_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Catalog([Course("C949", "A", 4), Course("c949", "B", 4)])

    def test_total_units_ignores_unknown_codes(self) -> None:
        catalog = sample_catalog()
        self.assertEqual(catalog.total_units(["C949", "D197", "Z999"]), 5)

    def test_units_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            Course("C100", "Zero", 0)


if __name__ == "__main__":
    unittest.main()
