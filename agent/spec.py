"""Build specification dataclasses (pinned interface, see agent/ARCHITECTURE.md).

Also provides JSON round-tripping (spec_to_json / spec_from_json) — the wire
format the brain reads from `pipeline parse` and feeds back to `pipeline spec`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from typing import Literal


@dataclass
class ObjectSpec:
    """One distinct printable object (count>1 means N separate copies)."""

    name: str
    kind: Literal["mechanical", "organic"]
    dims_mm: dict  # e.g. {"outer_d": 20, "thickness": 5, "teeth": 20, "module": 0.9, "bore": 5}
    count: int = 1
    tolerances_mm: float = 0.2
    notes: str = ""


@dataclass
class BuildSpec:
    """The full parsed build request: what to model, from what source."""

    objects: list[ObjectSpec]
    source_request: str
    reference_images: list[str] = field(default_factory=list)


# --- JSON round-tripping (unknown keys are ignored for forward-compat) ---

_OBJECT_FIELDS = {f.name for f in fields(ObjectSpec)}
_BUILD_FIELDS = {f.name for f in fields(BuildSpec)}


def spec_to_dict(spec: BuildSpec) -> dict:
    """BuildSpec -> plain dict (JSON-serializable)."""
    return asdict(spec)


def spec_from_dict(d: dict) -> BuildSpec:
    """Plain dict -> BuildSpec; unknown keys are dropped, defaults fill gaps."""
    objects = [
        ObjectSpec(**{k: v for k, v in o.items() if k in _OBJECT_FIELDS})
        for o in d.get("objects", [])
    ]
    top = {k: v for k, v in d.items() if k in _BUILD_FIELDS and k != "objects"}
    return BuildSpec(objects=objects, **top)


def spec_to_json(spec: BuildSpec, *, indent: int = 2) -> str:
    """BuildSpec -> pretty JSON string."""
    return json.dumps(spec_to_dict(spec), indent=indent, ensure_ascii=False)


def spec_from_json(s: str) -> BuildSpec:
    """JSON string -> BuildSpec."""
    return spec_from_dict(json.loads(s))
