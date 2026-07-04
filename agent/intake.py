"""Intake: heuristic request -> BuildSpec draft (stage 3, "understand").

DELIBERATELY DUMB AND HONEST: no LLM here. This is regex number-pulling that
gives the Claude brain a starting draft (`pipeline parse`); the brain corrects
it with real language understanding. Dimensions that are not literally present
in the text are NOT invented — they are left out of dims_mm so clarify.py can
flag them as open questions.
"""

from __future__ import annotations

import os
import re

from agent.spec import BuildSpec, ObjectSpec

_NUM = r"(\d+(?:[.,]\d+)?)"

# Cues that the object is organic (figurine/sculpt) rather than dimensional CAD.
_ORGANIC_RE = re.compile(
    r"фигурк|статуэтк|звер[её]к|animal|figurine|figure of|statuette|organic"
    r"|toy character|котик|собачк|dragon|дракон",
    re.IGNORECASE,
)

# Cues that the object is a gear (drives naming + gear-specific clarify checks).
_GEAR_RE = re.compile(r"шестер\w*|gear\w*|зубчат\w*|cogwheel", re.IGNORECASE)

# (pattern, dim-key) — tried in order on a working copy of the text; every match
# is blanked out so later, less specific patterns can't re-claim its number
# (e.g. "толщина 5мм" must not later read as a bare "5мм" diameter).
_DIM_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"толщин\w*\s*[=:]?\s*" + _NUM + r"\s*(?:mm|мм)?", re.I), "thickness"),
    (re.compile(r"thickness\s*[=:]?\s*" + _NUM + r"\s*(?:mm|мм)?", re.I), "thickness"),
    (re.compile(_NUM + r"\s*(?:mm|мм)?\s*thick\b", re.I), "thickness"),
    (re.compile(r"(?:module|модул[ья]\w*)\s*[=:]?\s*" + _NUM, re.I), "module"),
    (re.compile(r"\bm\s*=\s*" + _NUM, re.I), "module"),
    (re.compile(_NUM + r"\s*(?:зуб\w*|teeth|tooth)", re.I), "teeth"),
    (re.compile(r"(?:зубьев|teeth)\s*[=:]?\s*(\d+)", re.I), "teeth"),
    (re.compile(r"(?:отверсти\w*|bore|hole)\s*[=:]?\s*" + _NUM + r"\s*(?:mm|мм)?", re.I), "bore"),
    (re.compile(r"[øØ⌀]\s*" + _NUM + r"\s*(?:mm|мм)?", re.I), "outer_d"),
    (re.compile(r"(?:диаметр\w*|diameter|dia\.?)\s*[=:]?\s*" + _NUM + r"\s*(?:mm|мм)?", re.I), "outer_d"),
]

# Bare "<N>mm" left over after all specific dims were blanked out.
_BARE_MM_RE = re.compile(_NUM + r"\s*(?:mm|мм)\b", re.IGNORECASE)

_COUNT_PATTERNS = [
    re.compile(
        r"(\d+)\s*(?:шестер\w*|gear\w*|фигурк\w*|figur\w*|детал\w*|part(?:s)?\b"
        r"|cop(?:y|ies)|штук\w*|шт\b|pcs|pieces)",
        re.IGNORECASE,
    ),
    re.compile(r"[x×]\s*(\d+)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s*[x×](?=\s|$)", re.IGNORECASE),
]


def _to_float(s: str) -> float:
    return float(s.replace(",", "."))


def _split_env_paths(var: str) -> list[str]:
    return [p for p in os.environ.get(var, "").split() if p]


def parse_request(
    text: str,
    images: list[str] | None = None,
    audio: list[str] | None = None,
) -> BuildSpec:
    """Heuristic parse of a print request into a draft BuildSpec.

    Pulls only what is literally in the text (numbers with unit/keyword cues);
    missing dimensions stay missing so clarify can ask about them.
    """
    text = text or ""
    work = text  # working copy; matched spans get blanked out

    def blank(m: re.Match) -> None:
        nonlocal work
        work = work[: m.start()] + " " * (m.end() - m.start()) + work[m.end() :]

    dims: dict[str, float] = {}
    for pattern, key in _DIM_PATTERNS:
        m = pattern.search(work)
        if m and key not in dims:
            dims[key] = _to_float(m.group(1))
            blank(m)

    count = 1
    for pattern in _COUNT_PATTERNS:
        m = pattern.search(work)
        if m:
            count = int(m.group(1))
            blank(m)
            break

    organic = bool(_ORGANIC_RE.search(text))
    kind = "organic" if organic else "mechanical"

    # Any leftover bare "<N>mm" — overall size: outer_d for mechanical parts,
    # a generic "size" for organic ones.
    m = _BARE_MM_RE.search(work)
    if m:
        key = "size" if organic else "outer_d"
        if key not in dims and "outer_d" not in dims:
            dims[key] = _to_float(m.group(1))
        blank(m)

    if organic:
        name = "figurine"
        dims.pop("teeth", None)  # gear dims make no sense on an organic object
    elif _GEAR_RE.search(text) or "teeth" in dims or "module" in dims:
        name = "gear"
    else:
        name = "part"

    if "teeth" in dims:
        dims["teeth"] = int(dims["teeth"])

    ref_images = list(images) if images else _split_env_paths("PRINT_AGENT_IMAGES")
    audio_paths = list(audio) if audio else _split_env_paths("PRINT_AGENT_AUDIO")

    source = text.strip()
    if audio_paths:  # BuildSpec has no audio field — surface it for the brain
        source += " [audio: " + " ".join(audio_paths) + "]"

    obj = ObjectSpec(name=name, kind=kind, dims_mm=dims, count=count)
    return BuildSpec(objects=[obj], source_request=source, reference_images=ref_images)
