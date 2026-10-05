"""Course unlocking: determine which courses are unlocked by completing a given course."""

from __future__ import annotations

from catalog.catalog import Catalog
from catalog.codes import normalize_code


def unlocked_by(code: str, catalog: Catalog) -> list[str]:
    """Return sorted list of course codes that have the given course as a prerequisite.

    Args:
        code: A course code (will be normalized)
        catalog: The course catalog containing course and prerequisite information

    Returns:
        A sorted list of course codes that have the given course as a prerequisite

    Raises:
        ValueError: If the code does not exist in the catalog
        InvalidCourseCode: If the code is malformed (from normalize_code)
    """
    # Normalize the code (may raise InvalidCourseCode)
    normalized_code = normalize_code(code)

    # Validate that the code exists in the catalog
    if catalog.get(normalized_code) is None:
        raise ValueError(f"Course code not found in catalog: {normalized_code}")

    # Find all courses that have this code as a prerequisite
    unlocked: list[str] = []
    for course_code, course in catalog._courses.items():
        if normalized_code in course.prerequisites:
            unlocked.append(course_code)

    # Return sorted list
    return sorted(unlocked)
