"""Public-API surface snapshot for whats_that_code.

Emits a normalized, deterministic JSON description of the package's public API
(modules, functions + signatures, classes + public methods, public attribute
names) using griffe. Used to detect *accidental* API changes — the library has
~2,000 downloads/month and the public surface is a contract (see spec/spec.md).

Usage:
    python scripts/api_snapshot.py            # write spec/api_surface.json
    python scripts/api_snapshot.py --check    # compare; exit 1 if it changed

When a change is intentional, re-run without --check to update the snapshot and
review the diff in code review.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import griffe

PACKAGE = "whats_that_code"
SNAPSHOT = Path(__file__).resolve().parent.parent / "spec" / "api_surface.json"


def _is_public(name: str) -> bool:
    return not name.startswith("_")


def _param(p: Any) -> dict[str, Any]:
    kind = p.kind.value if hasattr(p.kind, "value") else str(p.kind)
    default = None if p.default is None else str(p.default)
    annotation = None if p.annotation is None else str(p.annotation)
    return {"name": p.name, "kind": kind, "annotation": annotation, "default": default}


def _function(func: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "parameters": [_param(p) for p in func.parameters],
        "returns": None if func.returns is None else str(func.returns),
    }


def _class(cls: Any) -> dict[str, Any]:
    methods = {}
    for name, member in cls.members.items():
        if not _is_public(name) or getattr(member, "is_alias", False):
            continue
        if getattr(member, "is_function", False):
            methods[name] = _function(member)
    return {"type": "class", "methods": methods}


def _module(mod: Any) -> dict[str, Any]:
    surface: dict[str, Any] = {}
    for name, member in mod.members.items():
        if not _is_public(name) or getattr(member, "is_alias", False):
            # skip private members and re-exported imports (aliases)
            continue
        if getattr(member, "is_module", False):
            continue  # submodules handled at the top level
        if getattr(member, "is_function", False):
            surface[name] = _function(member)
        elif getattr(member, "is_class", False):
            surface[name] = _class(member)
        elif getattr(member, "is_attribute", False):
            # record the public name only — values (data tables) intentionally omitted
            surface[name] = {"type": "attribute"}
    return surface


def build_surface() -> dict[str, Any]:
    root = griffe.load(PACKAGE, submodules=True)
    surface: dict[str, Any] = {}
    for path, mod in sorted(_iter_modules(root)):
        members = _module(mod)
        if members:
            surface[path] = members
    return surface


def _iter_modules(mod: Any):
    yield mod.path, mod
    for member in mod.members.values():
        if getattr(member, "is_alias", False):
            continue
        if getattr(member, "is_module", False):
            yield from _iter_modules(member)


def _dumps(surface: dict[str, Any]) -> str:
    return json.dumps(surface, indent=2, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    surface = build_surface()
    rendered = _dumps(surface)
    if "--check" in argv:
        if not SNAPSHOT.exists():
            print(f"No snapshot at {SNAPSHOT}; run `python scripts/api_snapshot.py` to create it.", file=sys.stderr)
            return 1
        current = SNAPSHOT.read_text(encoding="utf-8")
        if current != rendered:
            print(
                "Public API surface changed vs spec/api_surface.json.\n"
                "If intentional, run `make api-snapshot` and review the diff.\n",
                file=sys.stderr,
            )
            import difflib

            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                rendered.splitlines(keepends=True),
                fromfile="spec/api_surface.json",
                tofile="(current)",
            )
            sys.stderr.writelines(diff)
            return 1
        print("API surface matches snapshot.")
        return 0
    SNAPSHOT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {SNAPSHOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
