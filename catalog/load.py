"""CU (competency-unit) load checking for multi-term course plans."""

from __future__ import annotations

from catalog.catalog import Catalog


def check_term_loads(
    terms: list[list[str]],
    catalog: Catalog,
    max_units: int = 12,
) -> list[str]:
    """Return a list of error messages for terms that exceed the CU load limit.

    Args:
        terms: A list of terms, where each term is a list of course codes.
        catalog: The course catalog used to look up competency units.
        max_units: Maximum competency units allowed per term (default 12).

    Returns:
        A list of error messages for every term whose total CU count exceeds
        *max_units*. An empty list means every term is within the limit.

    Raises:
        ValueError: If *max_units* is not a positive integer.
    """
    if max_units <= 0:
        raise ValueError("max_units must be positive")

    errors: list[str] = []
    for term_num, term in enumerate(terms, start=1):
        total = catalog.total_units(term)
        if total > max_units:
            errors.append(
                f"Term {term_num} exceeds load limit: {total} CU (limit {max_units} CU)"
            )
    return errors
