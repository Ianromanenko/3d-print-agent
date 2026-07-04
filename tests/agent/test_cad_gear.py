"""CAD stage: the spur gear must exist, be watertight, and match the spec dims."""

from pathlib import Path

import pytest
import trimesh

from agent.generate.cad import generate_object, spur_gear
from agent.printability import check_and_repair
from agent.spec import ObjectSpec


@pytest.fixture(scope="module")
def gear_stl(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("cad") / "gear20.stl"
    # Ø20 outer: module = 20 / (20 + 2)
    return spur_gear(out, teeth=20, module=20 / 22, thickness=5.0, bore=5.0)


def test_gear_stl_exists(gear_stl: Path):
    assert gear_stl.is_file()
    assert gear_stl.stat().st_size > 10_000


def test_gear_watertight(gear_stl: Path):
    mesh = trimesh.load_mesh(gear_stl)
    assert mesh.is_watertight
    assert mesh.is_winding_consistent


def test_gear_dimensions(gear_stl: Path):
    mesh = trimesh.load_mesh(gear_stl)
    size = mesh.bounds[1] - mesh.bounds[0]
    assert size[0] == pytest.approx(20.0, abs=0.1)  # outer Ø
    assert size[1] == pytest.approx(20.0, abs=0.1)
    assert size[2] == pytest.approx(5.0, abs=0.01)  # thickness
    # the 5mm bore must be present (a solid disc of this size has more volume)
    solid_disc = 3.141592653589793 * 10.0**2 * 5.0
    assert mesh.volume < solid_disc * 0.95


def test_gear_passes_gate(gear_stl: Path, tmp_path: Path):
    res = check_and_repair(gear_stl, tmp_path)
    assert res.ok, res.report
    assert res.split_into == []


def test_generate_object_count_produces_n_files(tmp_path: Path):
    obj = ObjectSpec(
        name="g",
        kind="mechanical",
        dims_mm={"outer_d": 20.0, "teeth": 20, "thickness": 5.0, "bore": 5.0},
        count=3,
    )
    paths = generate_object(obj, tmp_path)
    assert len(paths) == 3
    assert len({p.name for p in paths}) == 3  # distinct filenames
    for p in paths:
        assert p.is_file() and p.stat().st_size > 10_000
