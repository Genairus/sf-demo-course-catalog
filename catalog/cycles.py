"""Cycle detection: find prerequisite cycles in the catalog."""

from __future__ import annotations

from catalog.catalog import Catalog


def find_prerequisite_cycles(catalog: Catalog) -> list[list[str]]:
    """Find all prerequisite cycles in the catalog.

    Uses DFS with three states (unvisited, visiting, visited) to detect cycles.
    A cycle exists when a course's prerequisite chain eventually leads back
    to itself.

    Args:
        catalog: The course catalog containing course and prerequisite information.

    Returns:
        A list of cycles, where each cycle is a list of course codes.
        Each cycle is normalized to start with the lex-smallest code.
        The list of cycles is sorted for deterministic output.
        For self-prerequisites (A -> A), returns [[A]].
        Unknown prerequisites are ignored (treated as having no outgoing edges).
    """
    # Get all course codes from the catalog
    # We need to access the internal dict since Catalog doesn't expose iteration
    all_courses = list(catalog._courses.keys())

    # Three states: 0 = unvisited, 1 = visiting (in current DFS path), 2 = visited
    state: dict[str, int] = {code: 0 for code in all_courses}

    # Store the parent pointer to reconstruct cycles
    parent: dict[str, str | None] = {}

    # Collect all found cycles (may have duplicates resolved during normalization)
    found_cycles: list[list[str]] = []

    def get_prereqs(code: str) -> list[str]:
        """Get prerequisites for a course, filtering out unknown courses."""
        course = catalog.get(code)
        if course is None:
            return []
        # Filter prerequisites to only include known courses
        return [p for p in course.prerequisites if p in catalog]

    def normalize_cycle(cycle_codes: list[str]) -> list[str]:
        """Normalize cycle to start with lex-smallest code."""
        if not cycle_codes:
            return cycle_codes
        # Find the minimum code
        min_code = min(cycle_codes)
        min_index = cycle_codes.index(min_code)
        # Rotate to start with minimum
        return cycle_codes[min_index:] + cycle_codes[:min_index]

    def dfs(node: str, path: list[str]) -> None:
        """DFS traversal to detect cycles."""
        if state[node] == 2:
            # Already fully processed
            return
        if state[node] == 1:
            # Found a cycle! Extract it from the path
            # Find where this node appears in the current path
            cycle_start = path.index(node)
            cycle = path[cycle_start:]
            if cycle:
                normalized = normalize_cycle(cycle)
                found_cycles.append(normalized)
            return

        # Mark as visiting
        state[node] = 1
        path.append(node)

        # Visit all prerequisites
        for prereq in get_prereqs(node):
            if prereq in state:
                dfs(prereq, path)

        # Done with this node, mark as visited
        path.pop()
        state[node] = 2

    # Run DFS from each unvisited node
    for code in all_courses:
        if state[code] == 0:
            dfs(code, [])

    # Deduplicate cycles (same normalized cycle may be found from different starting points)
    unique_cycles: set[tuple[str, ...]] = set()
    for cycle in found_cycles:
        unique_cycles.add(tuple(cycle))

    # Convert back to lists and sort for deterministic output
    result = [list(c) for c in unique_cycles]
    result.sort()

    return result
