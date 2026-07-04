"""Printability gate: repair + split of accidentally merged multi-body scenes."""

from pathlib import Path

import numpy as np
import trimesh

from agent.printability import check_and_repair


def _merged_two_body_stl(path: Path) -> Path:
    """One STL that (wrongly) contains two disconnected cubes."""
    a = trimesh.creation.box(extents=(10, 10, 10))
    b = trimesh.creation.box(extents=(8, 8, 8))
    b.apply_translation((30, 0, 0))
    trimesh.util.concatenate([a, b]).export(path)
    return path


def test_two_body_scene_splits_into_two(tmp_path: Path):
    stl = _merged_two_body_stl(tmp_path / "merged.stl")
    res = check_and_repair(stl, tmp_path / "gate")
    assert len(res.split_into) == 2
    assert res.ok, res.report
    assert sorted(p.name for p in res.split_into) == ["merged_body1.stl", "merged_body2.stl"]
    for p in res.split_into:
        m = trimesh.load_mesh(p)
        assert m.is_watertight
        assert len(m.split(only_watertight=False)) == 1  # each file is a single body
    assert res.output_paths == res.split_into


def test_clean_single_body_passes_untouched(tmp_path: Path):
    stl = tmp_path / "cube.stl"
    trimesh.creation.box(extents=(5, 5, 5)).export(stl)
    res = check_and_repair(stl, tmp_path / "gate")
    assert res.ok
    assert res.watertight and res.winding_consistent
    assert not res.repaired
    assert res.split_into == []
    assert res.output_paths == [stl]


def test_holed_mesh_reported_and_repaired(tmp_path: Path):
    """A box with one face removed is not watertight; the gate must try to repair it."""
    box = trimesh.creation.box(extents=(10, 10, 10))
    holed = trimesh.Trimesh(
        vertices=box.vertices.copy(), faces=np.delete(box.faces, 0, axis=0)
    )
    stl = tmp_path / "holed.stl"
    holed.export(stl)
    res = check_and_repair(stl, tmp_path / "gate")
    assert res.repaired
    assert res.watertight, res.report  # a single missing triangle is fillable
    assert res.ok
    assert res.output_paths[0].name == "holed_repaired.stl"
