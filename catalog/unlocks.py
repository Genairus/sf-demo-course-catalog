"""Course unlock tracking: find courses unlocked by completing a given course."""

from __future__ import annotations

from catalog.catalog import Catalog
from catalog.codes import InvalidCourseCode, normalize_code


def unlocked_by(code: str, catalog: Catalog) -> list[str]:
    """Return sorted list of courses that have the given code as a prerequisite.

    Args:
        code: Course code to check (will be normalized)
        catalog: The course catalog to search

    Returns:
        Sorted list of course codes that have the given course as a prerequisite

    Raises:
        ValueError: If the code is unknown (not in catalog)
        InvalidCourseCode: If the code is malformed
    """
    # Normalize the code (raises InvalidCourseCode if malformed)
    normalized = normalize_code(code)

    # Validate it exists in catalog
    if catalog.get(normalized) is None:
        raise ValueError(f"course code not found in catalog: {normalized}")

    # Collect courses that have this code as a prerequisite
    unlocked = []
    for course_code, course in catalog._courses.items():
        if normalized in course.prerequisites:
            unlocked.append(course_code)

    return sorted(unlocked)
