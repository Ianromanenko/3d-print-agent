"""Stage 6 (verify): offscreen renders are real images; bbox measurement and
spec-vs-measured deviation behave for correct and wrong-size specs."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from agent.generate.cad import spur_gear
from agent.render import render_object
from agent.spec import ObjectSpec
from agent.verify import build_rubric, deviation, measure

N_VIEWS = 4


@pytest.fixture(scope="module")
def gear_stl(tmp_path_factory) -> Path:
    """The canonical Ø20 gear: 20 teeth, module 20/22, 5mm thick, 5mm bore."""
    out = tmp_path_factory.mktemp("verify") / "gear20.stl"
    return spur_gear(out, teeth=20, module=20 / 22, thickness=5.0, bore=5.0)


@pytest.fixture(scope="module")
def gear_obj() -> ObjectSpec:
    return ObjectSpec(
        name="gear20",
        kind="mechanical",
        dims_mm={"outer_d": 20.0, "teeth": 20, "thickness": 5.0, "bore": 5.0},
    )


@pytest.fixture(scope="module")
def renders(gear_stl: Path, tmp_path_factory) -> list[Path]:
    return render_object(gear_stl, tmp_path_factory.mktemp("renders"), n_views=N_VIEWS)


def test_render_object_yields_n_views(renders: list[Path], gear_stl: Path):
    assert len(renders) == N_VIEWS
    assert len({p.name for p in renders}) == N_VIEWS  # distinct view names
    for p in renders:
        assert p.is_file() and p.suffix == ".png"
        assert p.name.startswith(gear_stl.stem + "_")


def test_renders_are_non_blank(renders: list[Path]):
    for p in renders:
        assert p.stat().st_size > 0
        img = np.asarray(Image.open(p).convert("RGB"))
        unique = np.unique(img.reshape(-1, 3), axis=0)
        assert len(unique) > 1, f"{p.name} is a single flat color"
        assert img.std() > 1.0, f"{p.name} has ~zero pixel variance"


def test_measure_bbox_of_gear(gear_stl: Path):
    m = measure(gear_stl)
    assert m["bbox_mm"]["x"] == pytest.approx(20.0, abs=0.3)
    assert m["bbox_mm"]["y"] == pytest.approx(20.0, abs=0.3)
    assert m["bbox_mm"]["z"] == pytest.approx(5.0, abs=0.3)
    assert m["outer_d_mm"] == pytest.approx(20.0, abs=0.3)
    assert m["body_count"] == 1


def test_deviation_correct_spec_within_tolerance(gear_obj: ObjectSpec, gear_stl: Path):
    dev = deviation(gear_obj, gear_stl)
    assert dev["within_tolerance"] is True
    for name in ("outer_d", "thickness"):
        assert abs(dev["dims"][name]["deviation_mm"]) <= gear_obj.tolerances_mm


def test_deviation_derives_outer_from_teeth_module(gear_stl: Path):
    """No outer_d in spec -> expected tip Ø = (teeth+2)*module = 20."""
    obj = ObjectSpec(
        name="g", kind="mechanical", dims_mm={"teeth": 20, "module": 20 / 22, "thickness": 5.0}
    )
    dev = deviation(obj, gear_stl)
    assert dev["dims"]["outer_d"]["expected_mm"] == pytest.approx(20.0)
    assert dev["within_tolerance"] is True


def test_deviation_wrong_size_spec_fails(gear_stl: Path):
    """A Ø30 spec against the Ø20 STL must NOT be within tolerance."""
    obj = ObjectSpec(
        name="wrong", kind="mechanical", dims_mm={"outer_d": 30.0, "thickness": 5.0}
    )
    dev = deviation(obj, gear_stl)
    assert dev["within_tolerance"] is False
    assert dev["dims"]["outer_d"]["within_tolerance"] is False
    assert dev["dims"]["outer_d"]["deviation_mm"] == pytest.approx(-10.0, abs=0.3)


def test_rubric_deterministic_filled_visual_null(
    gear_obj: ObjectSpec, gear_stl: Path, renders: list[Path]
):
    r = build_rubric(gear_obj, gear_stl, renders, gate_ok=True)
    rub = r["rubric"]
    # weights pinned by the blueprint
    assert {k: v["weight"] for k, v in rub.items()} == {
        "geometry": 35, "proportions": 25, "features": 20, "mechanical": 15, "printability": 5,
    }
    # visual slots left for the brain
    assert rub["geometry"]["score"] is None
    assert rub["features"]["score"] is None
    assert rub["geometry"]["_note"] == "score visually from renders"
    # deterministic slots filled: perfect gear -> full marks
    assert rub["proportions"]["score"] == pytest.approx(1.0)
    assert rub["mechanical"]["score"] == 1.0
    assert rub["printability"]["score"] == 1.0
    assert r["deterministic_subtotal"]["points"] == pytest.approx(45.0)
    assert r["deterministic_subtotal"]["max_points"] == 45
    assert r["renders"] == [str(p) for p in renders]


def test_rubric_gate_failure_zeroes_printability(gear_obj: ObjectSpec, gear_stl: Path):
    r = build_rubric(gear_obj, gear_stl, [], gate_ok=False)
    assert r["rubric"]["printability"]["score"] == 0.0
