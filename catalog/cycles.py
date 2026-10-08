"""Cycle detection in the prerequisite graph.

Provides functionality to detect circular dependencies in course prerequisites,
which would make a course plan impossible to complete.
"""

from __future__ import annotations

from catalog.catalog import Catalog


def find_prerequisite_cycles(catalog: Catalog) -> list[tuple[str, ...]]:
    """Find all cycles in the prerequisite graph.

    Uses depth-first search (DFS) to detect cycles in the directed graph
    formed by course prerequisites. Each cycle is returned as a tuple of
    course codes in order, starting from the lexicographically smallest
    code to ensure canonical representation.

    Args:
        catalog: The course catalog containing course and prerequisite information.

    Returns:
        A list of cycles found in the prerequisite graph. Each cycle is a
        tuple of course codes in order, starting with the lexicographically
        smallest code. The list is sorted lexicographically by the first
        element of each cycle. Returns an empty list if no cycles exist.

    Example:
        If CS101 requires CS102, and CS102 requires CS101, this returns
        [('CS101', 'CS102', 'CS101')].
    """
    cycles: list[tuple[str, ...]] = []

    # Access the internal courses dict to get all course codes.
    # Catalog does not expose public iteration, so we use getattr.
    courses_dict: dict[str, object] = getattr(catalog, "_courses", {})
    all_codes: set[str] = set(courses_dict.keys())

    # Track visit state: 0 = unvisited, 1 = in current path, 2 = fully processed
    state: dict[str, int] = {code: 0 for code in all_codes}

    def get_prereqs(code: str) -> list[str]:
        """Get prerequisites for a course code, filtering out unknown codes."""
        course = catalog.get(code)
        if course is None:
            return []
        return [p for p in course.prerequisites if p in all_codes]

    def dfs(code: str, path: list[str]) -> None:
        """DFS traversal to find cycles."""
        if state[code] == 2:
            # Already fully processed, no new cycles here
            return

        if state[code] == 1:
            # Found a cycle! Extract it from the path
            # Find where this cycle starts in our current path
            cycle_start_idx = path.index(code)
            cycle = path[cycle_start_idx:] + [code]
            # Normalize: rotate to start with lexicographically smallest element
            normalized_cycle = _normalize_cycle(cycle)
            cycles.append(normalized_cycle)
            return

        # Mark as being visited (in current path)
        state[code] = 1
        path.append(code)

        # Visit all prerequisites
        for prereq in get_prereqs(code):
            dfs(prereq, path)

        # Done with this node - mark as fully processed
        path.pop()
        state[code] = 2

    # Run DFS from each unvisited course
    for code in sorted(all_codes):  # Sort for deterministic order
        if state[code] == 0:
            dfs(code, [])

    # Deduplicate and sort cycles
    unique_cycles = list(set(cycles))
    unique_cycles.sort(key=lambda c: c[0])

    return unique_cycles


def _normalize_cycle(cycle: list[str]) -> tuple[str, ...]:
    """Normalize a cycle to start with the lexicographically smallest code.

    Args:
        cycle: A list of course codes forming a cycle, where the first
               and last elements are the same.

    Returns:
        A tuple of the cycle codes, rotated to start with the smallest code.
    """
    # Remove the duplicate last element for rotation
    cycle_codes = cycle[:-1]

    # Find the index of the minimum element
    min_idx = cycle_codes.index(min(cycle_codes))

    # Rotate the cycle to start with the minimum, then append the first element again
    rotated = cycle_codes[min_idx:] + cycle_codes[:min_idx] + [cycle_codes[min_idx]]
    return tuple(rotated)
