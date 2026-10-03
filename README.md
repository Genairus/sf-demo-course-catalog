# course-catalog

A small library for a university course catalog: course codes, competency units, and
prerequisites. It is the demo repository for the WGU Software Factory, so it is deliberately
small, dependency-free, and well tested. All data in it is synthetic.

## Layout

- `src/catalog/codes.py`: parsing and normalizing course codes (`C949`, `d335` -> `D335`).
- `src/catalog/models.py`: the `Course` dataclass.
- `src/catalog/catalog.py`: `Catalog`, a lookup of courses by code.
- `tests/`: `unittest` tests, one module per source module.

## Conventions

- Python 3.12 standard library only. No third-party packages (CI and the factory's sandbox
  have no network access to install any).
- Type hints on every public function. Prefer small pure functions and frozen dataclasses.
- Errors in user-supplied data (unknown codes, malformed codes) are reported, not raised,
  unless the function's docstring says it raises.
- Every change ships with `unittest` tests in `tests/test_<module>.py`.

## Commands

```
make build   # byte-compile the package
make test    # run the unit tests
make lint    # compile with warnings as errors
```
