from __future__ import annotations

from collections.abc import Iterable

from catalog.codes import normalize_code
from catalog.models import Course


class Catalog:
    """Courses by code. Codes are normalized on the way in and on lookup."""

    def __init__(self, courses: Iterable[Course] = ()) -> None:
        self._courses: dict[str, Course] = {}
        for course in courses:
            self.add(course)

    def add(self, course: Course) -> None:
        code = normalize_code(course.code)
        if code in self._courses:
            raise ValueError(f"duplicate course code: {code}")
        self._courses[code] = course

    def get(self, code: str) -> Course | None:
        """The course with this code, or None if the code is unknown or malformed."""
        try:
            return self._courses.get(normalize_code(code))
        except ValueError:
            return None

    def __contains__(self, code: object) -> bool:
        return isinstance(code, str) and self.get(code) is not None

    def __len__(self) -> int:
        return len(self._courses)

    def total_units(self, codes: Iterable[str]) -> int:
        """Total competency units for the given codes. Unknown codes count as zero."""
        return sum(course.competency_units for c in codes if (course := self.get(c)))
