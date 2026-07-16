#' ---
#' title: 8  05 Data Science Language Package Layer
#' ---
#' 

from __future__ import annotations

from pathlib import Path
from typing import Any


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

from typing import Any


def default_rproject(
    project_name: str,
    r_version: str,
    packages: list[str],
    git_dependencies: list[dict[str, str]] | None = None,
    library: str = ".rv/library",
) -> dict[str, Any]:
    """Return the default rv project configuration.

    Parameters
    ----------
    project_name
        Name of the project.

    r_version
        Required R version.

    packages
        CRAN-style package dependencies.

    git_dependencies
        Optional git dependencies.

    library
        Project-local rv library location. Relative paths are resolved
        relative to the project directory by rv.
    """

    dependencies: list[Any] = _dedupe(packages)

    if git_dependencies:
        dependencies.extend(git_dependencies)

    return {
        "library": library,
        "project": {
            "name": project_name,
            "r_version": r_version,
            "repositories": [
                {
                    "alias": "PPM",
                    "url": "https://packagemanager.posit.co/cran/latest",
                    "force_source": True
                }
            ],
            "dependencies": dependencies,
        },
    }


def default_pyproject(
    project_name: str,
    python_version: str,
    packages: list[str],
) -> dict[str, Any]:
    """Return the default uv project file data."""

    return {
        "project": {
            "name": project_name,
            "version": "0.1.0",
            "requires-python": f">={python_version}",
            "dependencies": _dedupe(packages),
        }
    }


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return '"' + value.replace('"', '\\"') + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        if all(not isinstance(item, dict) for item in value):
            return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    raise TypeError(f"Unsupported TOML value: {value!r}")


def _fallback_toml_dumps(data: dict[str, Any]) -> str:
    lines: list[str] = []

    def write_table(prefix: list[str], table: dict[str, Any]) -> None:
        if prefix:
            lines.append(f"[{'.'.join(prefix)}]")

        deferred: list[tuple[str, dict[str, Any]]] = []
        arrays: list[tuple[str, list[dict[str, Any]]]] = []

        for key, value in table.items():
            if isinstance(value, dict):
                deferred.append((key, value))
            elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
                arrays.append((key, value))
            else:
                lines.append(f"{key} = {_toml_value(value)}")

        lines.append("")

        for key, value in deferred:
            write_table(prefix + [key], value)

        for key, values in arrays:
            for item in values:
                lines.append(f"[[{'.'.join(prefix + [key])}]]")
                for item_key, item_value in item.items():
                    lines.append(f"{item_key} = {_toml_value(item_value)}")
                lines.append("")

    write_table([], data)
    return "\n".join(lines).rstrip() + "\n"


def _toml_dumps(data: dict[str, Any]) -> str:
    try:
        import tomli_w
    except ImportError:
        return _fallback_toml_dumps(data)

    return tomli_w.dumps(data)

def write_rproject_toml(path: Path, rproject: dict[str, Any]) -> Path:
    """Write rproject.toml idempotently."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_toml_dumps(rproject))
    return path


def write_pyproject_toml(path: Path, pyproject: dict[str, Any]) -> Path:
    """Write pyproject.toml idempotently."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_toml_dumps(pyproject))
    return path
