"""Clarify (stage 3, BLOCKING step 2 of BRAIN.md): restate + open questions.

`restate` mirrors BRAIN.md's confirmation format:
    Понял так: (1) шестерня Ø20 мм, m=1, 20 зубьев, толщина 5, отверстие 5 — ×6, раздельно.
`open_questions` flags only genuinely missing/ambiguous CRITICAL info — things
the CAD stage cannot proceed without. It does NOT nag about parameters with
sane defaults (tolerances, bore=0 meaning "no bore").
"""

from __future__ import annotations

import sys

from agent.spec import BuildSpec, ObjectSpec

# dims formatted in this order, everything else appended as k=v
_DIM_ORDER = ["outer_d", "size", "module", "teeth", "thickness", "bore"]


def _fmt_dim(key: str, v: float) -> str:
    v = int(v) if float(v) == int(v) else v
    return {
        "outer_d": f"Ø{v} мм",
        "size": f"{v} мм",
        "module": f"m={v}",
        "teeth": f"{v} зубьев",
        "thickness": f"толщина {v}",
        "bore": f"отверстие {v}",
    }.get(key, f"{key}={v}")


def _restate_object(obj: ObjectSpec) -> str:
    parts = [_fmt_dim(k, obj.dims_mm[k]) for k in _DIM_ORDER if k in obj.dims_mm]
    parts += [_fmt_dim(k, v) for k, v in obj.dims_mm.items() if k not in _DIM_ORDER]
    dims = ", ".join(parts) if parts else "размеры не указаны"
    kind = "органика" if obj.kind == "organic" else "механика"
    line = f"{obj.name} ({kind}): {dims}"
    if obj.count > 1:
        line += f" — ×{obj.count}, раздельно"
    elif obj.count == 1:
        line += " — ×1"
    if obj.notes:
        line += f" [{obj.notes}]"
    return line


def restate(spec: BuildSpec) -> str:
    """Human restatement of the parsed spec, per BRAIN.md's confirm format."""
    lines = ["Понял так:"]
    for i, obj in enumerate(spec.objects, 1):
        lines.append(f"  ({i}) {_restate_object(obj)}")
    return "\n".join(lines)


def _is_gear(obj: ObjectSpec) -> bool:
    d = obj.dims_mm
    return "gear" in obj.name.lower() or "teeth" in d or "module" in d


def open_questions(spec: BuildSpec) -> list[str]:
    """Genuinely missing/ambiguous critical info; empty list == safe to build."""
    qs: list[str] = []
    if not spec.objects:
        qs.append("Не понял, какие объекты печатать — опиши, что нужно.")
    for i, obj in enumerate(spec.objects, 1):
        tag = f"({i}) {obj.name}"
        d = obj.dims_mm
        if obj.count <= 0:
            qs.append(f"{tag}: сколько штук печатать?")
        if obj.kind == "organic":
            qs.append(
                f"{tag}: органика (Meshy) ещё не построена — стадия 4b; "
                "пока умею только код-CAD механику."
            )
            continue
        if _is_gear(obj):
            # any TWO of {teeth, module, outer_d} pin the geometry
            known = [k for k in ("teeth", "module", "outer_d") if k in d]
            if len(known) < 2:
                missing = [k for k in ("teeth", "module", "outer_d") if k not in d]
                qs.append(
                    f"{tag}: не хватает параметров зацепления — нужно минимум два из "
                    f"{{teeth, module, outer_d}}; отсутствуют: {', '.join(missing)}."
                )
        if "thickness" not in d:
            qs.append(f"{tag}: какая толщина (мм)?")
    return qs


_YES = {"", "y", "yes", "да", "ага", "ok", "ок", "+", "confirm", "подтверждаю"}


def confirm_interactive(spec: BuildSpec) -> BuildSpec | None:
    """TTY confirm gate. Returns the spec if confirmed, None if the user wants
    changes (the interactive Claude brain owns the real correction dialog).
    Non-TTY callers get the spec back unchanged (gating happens in `run`)."""
    if not sys.stdin.isatty():
        return spec
    print(restate(spec))
    qs = open_questions(spec)
    if qs:
        print("Вопросы:")
        for q in qs:
            print(f"  - {q}")
    print("Подтверди (y/да/Enter) или опиши правки:")
    try:
        answer = input("> ").strip().lower()
    except EOFError:
        return spec
    if answer in _YES:
        return spec
    return None
