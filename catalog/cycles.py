"""Cycle detection in prerequisite dependencies using DFS with three-color marking."""

from __future__ import annotations

from catalog.catalog import Catalog


def find_prerequisite_cycles(catalog: Catalog) -> list[list[str]]:
    """Find all prerequisite cycles in the catalog.

    Uses DFS with three-color marking (WHITE=unvisited, GRAY=in-progress, BLACK=completed)
    to detect back edges which indicate cycles in the prerequisite graph.

    Args:
        catalog: The course catalog containing course and prerequisite information

    Returns:
        A sorted list of cycles, where each cycle is a list of course codes.
        Cycles are normalized to their lexicographically smallest rotation
        and deduplicated.
    """
    # Three colors for DFS state
    WHITE = 0  # unvisited
    GRAY = 1   # in progress (on recursion stack)
    BLACK = 2  # completed

    color: dict[str, int] = {}
    cycles: set[tuple[str, ...]] = set()

    def normalize_cycle(cycle: list[str]) -> tuple[str, ...]:
        """Normalize cycle to lexicographically smallest rotation.

        The cycle is returned with the start element repeated at the end
        to form a complete cycle path (e.g., ['A', 'B', 'A']).
        """
        if not cycle:
            return tuple()
        # Find the lexicographically smallest rotation
        min_idx = 0
        for i in range(1, len(cycle)):
            if cycle[i] < cycle[min_idx]:
                min_idx = i
        # Rotate to start with smallest element
        rotated = cycle[min_idx:] + cycle[:min_idx]
        # Repeat the first element at the end to complete the cycle
        return tuple(rotated + [rotated[0]])

    def dfs(code: str, path: list[str]) -> None:
        """DFS traversal to detect cycles.

        Args:
            code: Current course code being visited
            path: Current recursion stack of course codes
        """
        # Initialize color for new nodes
        if code not in color:
            color[code] = WHITE

        # If node is already BLACK, it's completed - no cycle here
        if color[code] == BLACK:
            return

        # If node is GRAY, we found a back edge (cycle)
        if color[code] == GRAY:
            # Find where this node appears in the path to get the cycle
            if code in path:
                cycle_start = path.index(code)
                cycle = path[cycle_start:]
                # Normalize and add to cycles set
                normalized = normalize_cycle(cycle)
                if len(normalized) > 0:
                    cycles.add(normalized)
            return

        # Mark node as GRAY (in progress)
        color[code] = GRAY
        path.append(code)

        # Get the course and traverse its prerequisites
        course = catalog.get(code)
        if course is not None:
            for prereq in course.prerequisites:
                # Only traverse if prereq exists in catalog
                # Unknown prerequisites are silently skipped
                if prereq in catalog:
                    dfs(prereq, path)

        # Backtrack: remove from path and mark as BLACK (completed)
        path.pop()
        color[code] = BLACK

    # Start DFS from each course in the catalog
    for code in catalog._courses:
        if code not in color:
            dfs(code, [])

    # Convert set of tuples to sorted list of lists
    result = [list(cycle) for cycle in cycles]
    result.sort()
    return result
