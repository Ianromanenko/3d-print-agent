"""Code-CAD generators (build123d / OCCT) — one watertight STL per object.

spur_gear(): real involute spur gear (20 deg pressure angle, ISO-ish proportions:
addendum = 1.0*m, dedendum = 1.25*m). Outer (tip) diameter = (teeth + 2) * module.
For a target outer diameter D with z teeth, use module = D / (z + 2)
(e.g. Ø20 mm, 20 teeth -> module ~0.909, pitch Ø ~18.18).
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

from build123d import BuildPart, BuildSketch, Circle, Mode, Polygon, export_stl, extrude

from agent.spec import ObjectSpec

PRESSURE_ANGLE_DEG = 20.0
_FLANK_SAMPLES = 14
_ARC_SAMPLES = 5


def _involute_gear_outline(teeth: int, module: float) -> list[tuple[float, float]]:
    """CCW boundary points of a full involute spur gear profile in the XY plane."""
    z = teeth
    m = module
    alpha = math.radians(PRESSURE_ANGLE_DEG)
    rp = m * z / 2.0          # pitch radius
    rb = rp * math.cos(alpha)  # base radius
    ra = rp + 1.0 * m          # addendum (tip) radius
    rf = rp - 1.25 * m         # dedendum (root) radius
    if rf <= 0 or rb <= 0:
        raise ValueError(f"degenerate gear: teeth={z}, module={m}")

    def inv(a: float) -> float:
        return math.tan(a) - a

    half_p = math.pi / (2 * z)  # half tooth angular thickness at pitch circle

    def phi(r: float) -> float:
        """Angular offset of the involute flank from the tooth centerline at radius r."""
        a_r = math.acos(min(1.0, rb / r))
        return half_p + inv(alpha) - inv(a_r)

    r_start = max(rb, rf)  # involute exists only above the base circle
    pts: list[tuple[float, float]] = []

    def polar(r: float, a: float) -> tuple[float, float]:
        return (r * math.cos(a), r * math.sin(a))

    pitch_angle = 2 * math.pi / z
    for i in range(z):
        c = i * pitch_angle
        # rising flank (CCW: from root, -phi side, up to the tip)
        if rf < rb:
            pts.append(polar(rf, c - phi(rb)))  # radial stub root->base circle
        for k in range(_FLANK_SAMPLES + 1):
            r = r_start + (ra - r_start) * k / _FLANK_SAMPLES
            pts.append(polar(r, c - phi(r)))
        # tip arc
        for k in range(1, _ARC_SAMPLES + 1):
            a = -phi(ra) + 2 * phi(ra) * k / (_ARC_SAMPLES + 1)
            pts.append(polar(ra, c + a))
        # falling flank (tip back down to root, +phi side)
        for k in range(_FLANK_SAMPLES + 1):
            r = ra - (ra - r_start) * k / _FLANK_SAMPLES
            pts.append(polar(r, c + phi(r)))
        if rf < rb:
            pts.append(polar(rf, c + phi(rb)))
        # root arc over to the next tooth's rising flank
        a0 = c + phi(max(rb, rf) if rf >= rb else rb)
        a1 = c + pitch_angle - phi(max(rb, rf) if rf >= rb else rb)
        for k in range(1, _ARC_SAMPLES + 1):
            a = a0 + (a1 - a0) * k / (_ARC_SAMPLES + 1)
            pts.append(polar(rf, a))
    return pts


def spur_gear(out: Path, *, teeth: int, module: float, thickness: float, bore: float) -> Path:
    """Generate a watertight involute spur gear STL at `out`."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    outline = _involute_gear_outline(teeth, module)

    with BuildPart() as part:
        with BuildSketch():
            Polygon(*outline, align=None)
            if bore > 0:
                Circle(radius=bore / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=thickness)

    export_stl(part.part, str(out))
    return out


def generate_object(obj: ObjectSpec, out_dir: Path) -> list[Path]:
    """Generate ONE STL PER OBJECT; count>1 -> N distinct files."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    d = obj.dims_mm

    # A gear is pinned by any TWO of {teeth, module, outer_d}: tip Ø = (z+2)*m.
    if obj.kind == "mechanical" and (
        "teeth" in d or ("module" in d and "outer_d" in d)
    ):
        thickness = float(d.get("thickness", 5.0))
        bore = float(d.get("bore", 0.0))
        if "teeth" in d:
            teeth = int(d["teeth"])
        else:  # derive teeth from module + outer_d
            teeth = round(float(d["outer_d"]) / float(d["module"])) - 2
        if "module" in d:
            module = float(d["module"])
        elif "outer_d" in d:
            module = float(d["outer_d"]) / (teeth + 2)
        else:
            raise ValueError(f"{obj.name}: need 'module' or 'outer_d' in dims_mm")

        first = out_dir / (f"{obj.name}.stl" if obj.count == 1 else f"{obj.name}_1.stl")
        spur_gear(first, teeth=teeth, module=module, thickness=thickness, bore=bore)
        paths = [first]
        for i in range(2, obj.count + 1):  # identical copies -> just copy the file
            copy = out_dir / f"{obj.name}_{i}.stl"
            shutil.copyfile(first, copy)
            paths.append(copy)
        return paths

    raise NotImplementedError(
        f"{obj.name}: no CAD generator for kind={obj.kind}, dims={sorted(d)} "
        "(organic -> generate/mesh.py, stage 4b)"
    )
