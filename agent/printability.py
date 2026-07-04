"""Printability gate: watertight + winding checks, auto-repair, split of merged bodies.

trimesh does the checking/repair; manifold3d independently verifies the mesh is a
valid manifold (the stricter of the two — it is what slicers ultimately need).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh


@dataclass
class GateResult:
    ok: bool
    watertight: bool
    winding_consistent: bool
    repaired: bool
    split_into: list[Path]  # non-empty only when the file held >1 disconnected body
    report: str
    # Files to feed to the next stage: the splits, the repaired file, or the original.
    output_paths: list[Path] = field(default_factory=list)


def _is_manifold3d_valid(mesh: trimesh.Trimesh) -> bool:
    """Strict manifold check via manifold3d (returns False when it rejects the mesh)."""
    try:
        import manifold3d

        m = manifold3d.Manifold(
            manifold3d.Mesh(
                vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
                tri_verts=np.asarray(mesh.faces, dtype=np.uint32),
            )
        )
        return m.status() == manifold3d.Error.NoError and m.num_tri() > 0
    except Exception:
        return False


def _repair(mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, list[str]]:
    """In-place trimesh repair passes; returns (mesh, list of applied actions)."""
    actions: list[str] = []
    if not (mesh.is_watertight and mesh.is_winding_consistent):
        before = (mesh.is_watertight, mesh.is_winding_consistent)
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.update_faces(mesh.unique_faces())
        mesh.remove_unreferenced_vertices()
        mesh.merge_vertices()
        trimesh.repair.fix_winding(mesh)
        trimesh.repair.fix_inversion(mesh)
        trimesh.repair.fix_normals(mesh)
        if not mesh.is_watertight:
            trimesh.repair.fill_holes(mesh)
        after = (mesh.is_watertight, mesh.is_winding_consistent)
        if after != before:
            actions.append(f"trimesh repair: watertight/winding {before} -> {after}")
    return mesh, actions


def check_and_repair(stl: Path, out_dir: Path) -> GateResult:
    """Gate one STL: assert watertight AND winding-consistent, auto-repair,
    split multi-body files into separate STLs (one object per file)."""
    stl = Path(stl)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # default processing merges STL's duplicated vertices — required for
    # meaningful connectivity (split) and watertight checks
    mesh = trimesh.load_mesh(stl)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
        mesh.merge_vertices()

    lines = [f"gate: {stl.name} — {len(mesh.faces)} faces, {len(mesh.vertices)} verts"]
    repaired = False
    split_into: list[Path] = []

    bodies = mesh.split(only_watertight=False)
    if len(bodies) > 1:
        lines.append(f"MULTI-BODY: {len(bodies)} disconnected bodies -> splitting")
        results: list[tuple[trimesh.Trimesh, list[str]]] = [_repair(b) for b in bodies]
        for i, (body, actions) in enumerate(results, 1):
            p = out_dir / f"{stl.stem}_body{i}.stl"
            body.export(p)
            split_into.append(p)
            repaired |= bool(actions)
            lines.append(
                f"  body{i}: watertight={body.is_watertight} "
                f"winding={body.is_winding_consistent} -> {p.name}"
                + (f" ({'; '.join(actions)})" if actions else "")
            )
        watertight = all(b.is_watertight for b, _ in results)
        winding = all(b.is_winding_consistent for b, _ in results)
        manifold_ok = all(_is_manifold3d_valid(b) for b, _ in results)
        outputs = list(split_into)
    else:
        mesh, actions = _repair(mesh)
        repaired = bool(actions)
        lines.extend(actions)
        watertight = mesh.is_watertight
        winding = mesh.is_winding_consistent
        manifold_ok = _is_manifold3d_valid(mesh)
        if repaired:
            fixed = out_dir / f"{stl.stem}_repaired.stl"
            mesh.export(fixed)
            lines.append(f"repaired mesh written -> {fixed.name}")
            outputs = [fixed]
        else:
            outputs = [stl]

    ok = watertight and winding and manifold_ok
    lines.append(
        f"watertight={watertight} winding_consistent={winding} "
        f"manifold3d_valid={manifold_ok} => {'OK' if ok else 'FAIL'}"
    )
    return GateResult(
        ok=ok,
        watertight=watertight,
        winding_consistent=winding,
        repaired=repaired,
        split_into=split_into,
        report="\n".join(lines),
        output_paths=outputs,
    )
