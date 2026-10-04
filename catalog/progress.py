"""Progress tracking: determine which courses are available based on completed courses."""

from __future__ import annotations

from collections.abc import Iterable

from catalog.catalog import Catalog
from catalog.codes import normalize_code


def available_courses(completed: Iterable[str], catalog: Catalog) -> list[str]:
    """Return sorted list of course codes that are available to take.

    A course is available if:
    - It has not already been completed
    - All of its prerequisites are in the completed set

    Args:
        completed: Iterable of completed course codes (will be normalized)
        catalog: The course catalog containing course and prerequisite information

    Returns:
        A sorted list of available course codes

    Raises:
        ValueError: If any completed code does not exist in the catalog
    """
    # Normalize all completed codes and build a set for O(1) lookup
    completed_set: set[str] = set()
    for raw_code in completed:
        code = normalize_code(raw_code)
        # Validate that each completed code exists in catalog
        if catalog.get(code) is None:
            raise ValueError(f"Course code not found in catalog: {code}")
        completed_set.add(code)

    # Find all available courses
    available: list[str] = []
    for code, course in catalog._courses.items():
        # Skip if already completed
        if code in completed_set:
            continue
        # Check if all prerequisites are completed
        if all(prereq in completed_set for prereq in course.prerequisites):
            available.append(code)

    # Return sorted list
    return sorted(available)
