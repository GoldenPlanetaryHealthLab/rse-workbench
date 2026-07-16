#' ---
#' title: 7  04 Scientific System Dependency Layer
#' ---
#' 

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def default_spack_env(
    *,
    r_version: str,
    python_version: str,
    extra_specs: list[str] | None = None,
    default_specs: list[str] = [
        "libiconv",
        "ncurses",
        "openblas",
        "curl",
        "openssl",
        "pkgconf",
        "abseil-cpp",
        "zlib",
        "zlib-ng+compat",
        "cmake",
        "gmake",
        "git",
        "libx11",
        "libxml2",
        "freetype",
        "libjpeg",
        "libjpeg-turbo",
        "libpng",
        "libtiff",
        "libwebp +libwebpmux",
        "icu4c",
        "fontconfig",
        "fribidi",
        "harfbuzz",
        "libgit2",
        "cairo",
        "readline",
        "libuv",
    ]
) -> dict[str, Any]:
    """Return a default system-dependency-only Spack environment."""

    specs = [f"r@{r_version}", f"python@{python_version}"]
    specs.extend(default_specs)
    specs.extend(extra_specs or [])

    return {
        "spack": {
            "specs": _dedupe(specs),
            "view": "/work/.spack-env/view",
            "config": {
                "install_tree": {"root": "/work/.spack-env/install"},
                "source_cache": "/work/.spack/cache/source",
                "misc_cache": "/work/.spack/cache/misc",
                "build_stage": ["/work/.spack/stage"],
                "shared_linking": {
                    "type": "rpath",
                    "missing_library_policy": "error",
                },
            },
        }
    }


def write_spack_yaml(path: Path, spack_env: dict[str, Any]) -> Path:
    """Write spack.yaml idempotently, creating parent directories first."""
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(spack_env, sort_keys=False))
    return path
