from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Course:
    """A catalog course. `prerequisites` are course codes that must be completed first."""

    code: str
    title: str
    competency_units: int
    prerequisites: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.competency_units <= 0:
            raise ValueError(f"{self.code}: competency_units must be positive")
