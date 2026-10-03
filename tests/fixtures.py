"""A small synthetic catalog shared by the tests."""

from catalog import Catalog, Course


def sample_catalog() -> Catalog:
    return Catalog(
        [
            Course("C949", "Data Structures and Algorithms I", 4),
            Course("C950", "Data Structures and Algorithms II", 4, prerequisites=("C949",)),
            Course("D335", "Introduction to Programming in Python", 3),
            Course("D197", "Version Control", 1),
            Course("D333", "Ethics in Technology", 3),
            Course("D287", "Java Frameworks", 3, prerequisites=("D335", "D197")),
        ]
    )
