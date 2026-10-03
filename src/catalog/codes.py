"""Course codes: one uppercase letter followed by three or four digits (e.g. C949, D335)."""

from __future__ import annotations

import re

_CODE = re.compile(r"[A-Z][0-9]{3,4}")


class InvalidCourseCode(ValueError):
    pass


def normalize_code(raw: str) -> str:
    """Return the canonical form of a course code, or raise InvalidCourseCode.

    Surrounding whitespace is ignored and letters are uppercased: " d335 " -> "D335".
    """
    code = raw.strip().upper()
    if not _CODE.fullmatch(code):
        raise InvalidCourseCode(f"not a course code: {raw!r}")
    return code


def is_valid_code(raw: str) -> bool:
    try:
        normalize_code(raw)
    except InvalidCourseCode:
        return False
    return True
