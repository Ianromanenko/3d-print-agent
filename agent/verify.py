"""Self-check rubric (stage 6) — the deterministic half of BRAIN.md step 5.

Measures each gated STL (trimesh bbox), compares against the ObjectSpec dims,
renders multi-angle PNGs (render.py), and assembles the ≥95% rubric with the
blueprint weights (blueprint/agent-architecture.md «Рубрика самопроверки»):

    geometry 35 / proportions 25 / features 20 / mechanical 15 / printability 5

Deterministic slots (proportions, mechanical, printability) are FILLED here;
visual slots (geometry, features) stay `null` — the Claude brain scores them
by looking at the renders with its own vision, then computes the weighted total.
"""

from __future__ import annotations

from pathlib import Path

import trimesh

from agent.render import render_object
from agent.spec import ObjectSpec

# Rubric weights (must add up to 100) — pinned in blueprint/agent-architecture.md.
WEIGHTS = {
    "geometry": 35,  # silhouette matches the request — VISUAL
    "proportions": 25,  # measured bbox vs spec dims — deterministic
    "features": 20,  # all requested elements present — VISUAL
    "mechanical": 15,  # part count + separateness — deterministic (from spec + gate)
    "printability": 5,  # watertight/manifold gate passed — deterministic
}
THRESHOLD_PCT = 95
_VISUAL_NOTE = "score visually from renders"


def measure(stl: Path) -> dict:
    """Measure the mesh: bbox extents in mm (x/y/z) + gear-style outer diameter."""
    mesh = trimesh.load_mesh(Path(stl))
    ext = (mesh.bounds[1] - mesh.bounds[0]).tolist()
    return {
        "bbox_mm": {"x": ext[0], "y": ext[1], "z": ext[2]},
        # for a gear (or any part printed flat) the outer Ø is the XY footprint
        "outer_d_mm": max(ext[0], ext[1]),
        "body_count": len(mesh.split(only_watertight=False)),
        "faces": len(mesh.faces),
    }


def _expected_dims(obj: ObjectSpec) -> dict:
    """Spec dims we can check against a bbox: outer_d (mm) and thickness (mm).

    outer_d is derived from teeth/module when absent: tip Ø = (teeth + 2) * module.
    """
    d = obj.dims_mm
    expected: dict[str, float] = {}
    if "outer_d" in d:
        expected["outer_d"] = float(d["outer_d"])
    elif "teeth" in d and "module" in d:
        expected["outer_d"] = (int(d["teeth"]) + 2) * float(d["module"])
    if "thickness" in d:
        expected["thickness"] = float(d["thickness"])
    return expected


def deviation(obj: ObjectSpec, stl: Path) -> dict:
    """Per-dim measured-vs-spec deviation (mm and %) + a within-tolerance verdict."""
    measured = measure(stl)
    got = {
        "outer_d": measured["outer_d_mm"],
        "thickness": measured["bbox_mm"]["z"],
    }
    tol = float(obj.tolerances_mm)
    dims: dict[str, dict] = {}
    for name, exp in _expected_dims(obj).items():
        dev = got[name] - exp
        dims[name] = {
            "expected_mm": exp,
            "measured_mm": got[name],
            "deviation_mm": dev,
            "deviation_pct": (dev / exp * 100.0) if exp else 0.0,
            "within_tolerance": abs(dev) <= tol,
        }
    return {
        "dims": dims,
        "tolerance_mm": tol,
        "within_tolerance": all(v["within_tolerance"] for v in dims.values()),
    }


def _proportions_score(dev: dict) -> float:
    """0..1 from deviation: 1.0 within tolerance, linear decay to 0 at 5x tolerance."""
    if not dev["dims"]:
        return 0.0  # nothing measurable in the spec -> can't award proportion points
    tol = dev["tolerance_mm"]
    scores = []
    for v in dev["dims"].values():
        over = max(0.0, abs(v["deviation_mm"]) - tol)
        scores.append(max(0.0, 1.0 - over / (4.0 * tol)) if tol > 0 else float(over == 0.0))
    return min(scores)  # the worst dimension caps the score


def build_rubric(
    obj: ObjectSpec, stl: Path, renders: list[Path], gate_ok: bool
) -> dict:
    """Assemble the rubric: deterministic slots filled, visual slots null."""
    stl = Path(stl)
    measured = measure(stl)
    dev = deviation(obj, stl)
    single_body = measured["body_count"] == 1

    criteria = {
        "geometry": {
            "weight": WEIGHTS["geometry"],
            "score": None,
            "_note": _VISUAL_NOTE,
        },
        "proportions": {
            "weight": WEIGHTS["proportions"],
            "score": round(_proportions_score(dev), 4),
            "detail": "measured bbox vs spec dims (see 'deviation')",
        },
        "features": {
            "weight": WEIGHTS["features"],
            "score": None,
            "_note": _VISUAL_NOTE,
        },
        "mechanical": {
            "weight": WEIGHTS["mechanical"],
            "score": 1.0 if single_body else 0.0,
            "detail": (
                f"this STL is {'a single separate body' if single_body else 'MULTI-BODY'}"
                f" ({measured['body_count']} bodies); spec count={obj.count}"
                " (one file per copy is enforced by generate/gate)"
            ),
        },
        "printability": {
            "weight": WEIGHTS["printability"],
            "score": 1.0 if gate_ok else 0.0,
            "detail": f"printability gate {'passed' if gate_ok else 'FAILED'}",
        },
    }
    det_points = sum(
        c["weight"] * c["score"] for c in criteria.values() if c["score"] is not None
    )
    det_max = sum(c["weight"] for c in criteria.values() if c["score"] is not None)
    return {
        "object": obj.name,
        "stl": str(stl),
        "renders": [str(p) for p in renders],
        "measured": measured,
        "deviation": dev,
        "rubric": criteria,
        "deterministic_subtotal": {
            "points": round(det_points, 2),
            "max_points": det_max,
            "of_total": 100,
        },
        "threshold_pct": THRESHOLD_PCT,
        "_next": (
            "brain: view the render PNGs, fill geometry/features scores (0..1), "
            "total = sum(weight*score); release only if total >= threshold_pct"
        ),
    }


def verify_object(obj: ObjectSpec, stl: Path, out_dir: Path, gate_ok: bool) -> dict:
    """Render + measure + rubric for one gated STL. Returns the rubric dict."""
    renders = render_object(Path(stl), Path(out_dir))
    return build_rubric(obj, stl, renders, gate_ok)
