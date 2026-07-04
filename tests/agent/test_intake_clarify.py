"""Stage 3: intake (heuristic parse), clarify (open questions), spec JSON round-trip."""

from agent.clarify import open_questions, restate
from agent.intake import parse_request
from agent.spec import BuildSpec, ObjectSpec, spec_from_json, spec_to_json


def test_parse_full_gear_request_ru():
    spec = parse_request("6 шестерён Ø20мм module 1 толщина 5 отверстие 5")
    assert len(spec.objects) == 1
    obj = spec.objects[0]
    assert obj.kind == "mechanical"
    assert obj.count == 6
    assert obj.dims_mm["outer_d"] == 20
    assert obj.dims_mm["module"] == 1
    assert obj.dims_mm["thickness"] == 5
    assert obj.dims_mm["bore"] == 5


def test_parse_organic_figurine():
    spec = parse_request("напечатай фигурку котика 40мм")
    assert spec.objects[0].kind == "organic"


def test_parse_does_not_invent_dims():
    spec = parse_request("шестерня")
    assert spec.objects[0].dims_mm == {}  # nothing was stated -> nothing parsed


def test_open_questions_gear_missing_module_and_teeth():
    spec = BuildSpec(
        objects=[
            ObjectSpec(name="gear", kind="mechanical", dims_mm={"outer_d": 20.0}, count=1)
        ],
        source_request="шестерня Ø20",
    )
    qs = open_questions(spec)
    assert qs  # gear geometry underdetermined (only one of teeth/module/outer_d)


def test_open_questions_empty_for_fully_specified_gear():
    spec = BuildSpec(
        objects=[
            ObjectSpec(
                name="gear",
                kind="mechanical",
                dims_mm={"outer_d": 20.0, "module": 1.0, "teeth": 20, "thickness": 5.0, "bore": 5.0},
                count=6,
            )
        ],
        source_request="6 шестерён Ø20 m=1 20 зубьев толщина 5",
    )
    assert open_questions(spec) == []


def test_open_questions_flags_organic_stage4b():
    spec = parse_request("напечатай фигурку котика 40мм")
    qs = open_questions(spec)
    assert any("4b" in q for q in qs)


def test_spec_json_roundtrip():
    spec = BuildSpec(
        objects=[
            ObjectSpec(
                name="gear",
                kind="mechanical",
                dims_mm={"outer_d": 20.0, "module": 1.0, "teeth": 20, "thickness": 5.0},
                count=6,
                tolerances_mm=0.15,
                notes="test",
            ),
            ObjectSpec(name="figurine", kind="organic", dims_mm={"size": 40.0}),
        ],
        source_request="6 шестерён + фигурка",
        reference_images=["/tmp/ref.jpg"],
    )
    assert spec_from_json(spec_to_json(spec)) == spec


def test_restate_mentions_objects_and_count():
    spec = parse_request("6 шестерён Ø20мм module 1 толщина 5 отверстие 5")
    text = restate(spec)
    assert "(1)" in text and "×6" in text and "раздельно" in text
