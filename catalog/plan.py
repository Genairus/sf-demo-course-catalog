"""Validate a degree plan against a course catalog.

A *plan* is a list of terms; each term is a list of course-code strings.
The term index (0-based) determines when a course is taken.
"""

from __future__ import annotations

from catalog.catalog import Catalog
from catalog.codes import is_valid_code


def validate_plan(terms: list[list[str]], catalog: Catalog) -> list[str]:
    """Return a list of problem descriptions for the given plan.

    Checks performed, in order of discovery:
      - Malformed course codes (fail the is_valid_code() test).
      - Valid-format codes that are not in the catalog.
      - Prerequisites that appear in the plan in the same term or a later term
        than the course that requires them.
      - Prerequisites that do not appear anywhere in the plan.

    No exception is raised; all problems are collected and returned.
    """
    problems: list[str] = []

    # Build a mapping from course code -> term number (1-based for messages)
    # We only map codes that are valid-format so we can check prereqs later.
    code_to_term: dict[str, int] = {}
    for term_index, term_courses in enumerate(terms):
        term_number = term_index + 1
        for raw_code in term_courses:
            if is_valid_code(raw_code):
                normalized = raw_code.strip().upper()
                code_to_term[normalized] = term_number

    # Now validate each course in the plan.
    for term_index, term_courses in enumerate(terms):
        term_number = term_index + 1
        for raw_code in term_courses:
            # --- AC-4: Check for malformed codes ---
            if not is_valid_code(raw_code):
                problems.append(f'Malformed course code: "{raw_code}"')
                continue

            normalized = raw_code.strip().upper()

            # --- AC-4: Check for valid-format but unknown codes ---
            course = catalog.get(normalized)
            if course is None:
                problems.append(f"Unknown course code: {normalized}")
                continue

            # --- AC-2 & AC-3: Check prerequisites ---
            for prereq_code in course.prerequisites:
                prereq_normalized = prereq_code.strip().upper()
                if prereq_normalized not in code_to_term:
                    # AC-3: prerequisite not in the plan at all
                    problems.append(
                        f"{normalized} (term {term_number}): prerequisite"
                        f" {prereq_normalized} is not in the plan"
                    )
                elif code_to_term[prereq_normalized] >= term_number:
                    # AC-2: prerequisite is in the same or a later term
                    prereq_term = code_to_term[prereq_normalized]
                    problems.append(
                        f"{normalized} (term {term_number}): prerequisite"
                        f" {prereq_normalized} is in the same or a later term"
                        f" (term {prereq_term})"
                    )

    return problems
