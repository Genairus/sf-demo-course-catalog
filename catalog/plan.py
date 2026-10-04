"""Plan validation: check that all prerequisites are satisfied in proper order."""

from __future__ import annotations

from catalog.catalog import Catalog
from catalog.codes import InvalidCourseCode, normalize_code


def validate_plan(terms: list[list[str]], catalog: Catalog) -> list[str]:
    """Validate a multi-term course plan against catalog prerequisites.

    Args:
        terms: A list of terms, where each term is a list of course codes.
        catalog: The course catalog containing course and prerequisite information.

    Returns:
        A list of error messages. An empty list means the plan is valid.
        Error messages describe:
        - Malformed course codes
        - Unknown course codes
        - Prerequisites appearing in the same term as the course
        - Prerequisites appearing after the course in the term sequence
        - Prerequisites missing from the plan entirely
    """
    errors: list[str] = []
    seen_courses: set[str] = set()

    for term_index, term in enumerate(terms):
        current_term_courses: set[str] = set()

        for raw_code in term:
            # Try to normalize the course code
            try:
                code = normalize_code(raw_code)
            except InvalidCourseCode:
                errors.append(f"Malformed course code: {raw_code!r}")
                continue

            # Look up the course in the catalog
            course = catalog.get(code)
            if course is None:
                errors.append(f"Unknown course code: {code}")
                continue

            # Track the course in the current term
            current_term_courses.add(code)

            # Check each prerequisite
            for prereq in course.prerequisites:
                # Check if prerequisite appears in current term (same-term violation)
                if prereq in current_term_courses:
                    errors.append(
                        f"{code} scheduled in term {term_index + 1} but prerequisite "
                        f"{prereq} also appears in term {term_index + 1}"
                    )
                # Check if prerequisite was seen in earlier terms (ordering validation)
                elif prereq not in seen_courses:
                    # Scan all terms to see if prerequisite appears anywhere
                    prereq_found = False
                    prereq_term_index = -1
                    for idx, t in enumerate(terms):
                        for c in t:
                            try:
                                normalized = normalize_code(c)
                                if normalized == prereq:
                                    prereq_found = True
                                    prereq_term_index = idx
                                    break
                            except InvalidCourseCode:
                                pass
                        if prereq_found:
                            break

                    if prereq_found and prereq_term_index > term_index:
                        # Prerequisite appears later in the plan (ordering violation)
                        errors.append(
                            f"{code} scheduled in term {term_index + 1} but prerequisite "
                            f"{prereq} appears in term {prereq_term_index + 1}"
                        )
                    elif not prereq_found:
                        # Prerequisite is missing from the plan entirely
                        errors.append(
                            f"{code} requires prerequisite {prereq} which is not in the plan"
                        )

        # Add all courses from this term to the seen set after checking
        seen_courses.update(current_term_courses)

    return errors
