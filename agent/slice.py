"""Headless slicing -> .gcode.3mf (zip with Metadata/plate_1.gcode).

Attempt matrix (first success wins), per PLAN §10 fragility notes:
  binary:   Bambu Studio (pinned)  ->  OrcaSlicer (fallback)
  profiles: agent/profiles PETG HF overrides (`inherits` system presets)
            -> bundled system presets by path

Known blocker: the Bambu Studio 2.x CLI SEGFAULTs headless on macOS arm64
(upstream #8569/#3453 — `wxGetApp().plater()` on a null wxTheApp inside
PartPlateList::generate_print_polygon; no CLI flag avoids it). OrcaSlicer's
fork removed that call, ships the same bundled BBL A1 / PETG HF system
profiles, and takes the same CLI args, so it slices identically. A binary
that dies with a signal is skipped for the remaining attempts.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

from agent.config import BUNDLED_PROFILE_NAMES, bundled_profiles_dir, load_config

_MIN_GCODE_BYTES = 1000  # anything smaller is not a real sliced plate

# The CLI validates bed/filament compatibility; the implicit default (Cool Plate)
# rejects PETG, so the process config must always carry an explicit bed type.
_DEFAULT_BED_TYPE = "Textured PEI Plate"


class SliceError(RuntimeError):
    pass


def _resolve_inherits(path: Path, search_dirs: list[Path]) -> dict:
    """Flatten a preset's `inherits` chain (child keys win).

    The CLI does NOT resolve `inherits` in configs passed by path: it silently
    slices with defaults for every missing key — including printable_area
    (200x200), which makes arrange reject anything bigger than the A1-mini-ish
    default plate ("can not be arranged inside plate!").
    """
    cfg = json.loads(path.read_text())
    parent = cfg.pop("inherits", None)
    if parent is None:
        return cfg
    for d in search_dirs:
        p = d / f"{parent}.json"
        if p.is_file():
            base = _resolve_inherits(p, search_dirs)
            base.update(cfg)
            return base
    raise SliceError(f"{path.name}: parent preset '{parent}' not found in {search_dirs}")


def _merged_preset(src: Path, kind: str, bundled: Path, tmp_dir: Path) -> Path:
    """Write a fully-flattened copy of `src` into tmp_dir and return its path."""
    cfg = _resolve_inherits(src, [src.parent, bundled / kind])
    if kind == "process":
        cfg.setdefault("curr_bed_type", _DEFAULT_BED_TYPE)
    out = tmp_dir / f"{kind}_{src.stem}.json"
    out.write_text(json.dumps(cfg, indent=1))
    return out


def _run_cli(
    slicer_bin: Path,
    stls: list[Path],
    out: Path,
    machine_json: Path,
    process_json: Path,
    filament_json: Path,
    arrange: bool,
) -> subprocess.CompletedProcess:
    cmd = [
        str(slicer_bin),
        "--debug", "2",
        "--load-settings", f"{machine_json};{process_json}",
        "--load-filaments", str(filament_json),
        "--slice", "0",
        "--arrange", "1" if arrange else "0",
        "--export-3mf", out.name,
        "--outputdir", str(out.parent),
        *[str(p) for p in stls],
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600)


def _validate_gcode_3mf(out: Path) -> int:
    """Return byte size of Metadata/plate_1.gcode inside the archive (raises if bad)."""
    if not out.exists():
        raise SliceError(f"slicer produced no file at {out}")
    try:
        with zipfile.ZipFile(out) as z:
            info = z.getinfo("Metadata/plate_1.gcode")
    except (zipfile.BadZipFile, KeyError) as e:
        raise SliceError(f"{out.name}: no Metadata/plate_1.gcode inside ({e})")
    if info.file_size < _MIN_GCODE_BYTES:
        raise SliceError(f"{out.name}: plate_1.gcode is only {info.file_size} bytes")
    return info.file_size


def slice_objects(stls: list[Path], out: Path, *, arrange: bool = True) -> Path:
    """Slice STLs (as SEPARATE objects, auto-arranged) into a .gcode.3mf at `out`."""
    cfg = load_config()
    stls = [Path(p).resolve() for p in stls]
    for p in stls:
        if not p.is_file():
            raise FileNotFoundError(p)
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)

    errors: list[str] = []
    tmp_dir = Path(tempfile.mkdtemp(prefix="slice_presets_"))
    for slicer_bin in cfg.slicer_bins:
        bundled = bundled_profiles_dir(slicer_bin)
        machine = _merged_preset(
            bundled / "machine" / f"{BUNDLED_PROFILE_NAMES['machine']}.json",
            "machine", bundled, tmp_dir,
        )
        attempts = [
            (
                "PETG HF overrides (agent/profiles)",
                cfg.profiles_dir / "PETG_HF_process.json",
                cfg.profiles_dir / "PETG_HF_filament.json",
            ),
            (
                "bundled system presets (fallback)",
                bundled / "process" / f"{BUNDLED_PROFILE_NAMES['process']}.json",
                bundled / "filament" / f"{BUNDLED_PROFILE_NAMES['filament']}.json",
            ),
        ]
        for label, process_json, filament_json in attempts:
            tag = f"{slicer_bin.name} + {label}"
            process_json = _merged_preset(process_json, "process", bundled, tmp_dir)
            filament_json = _merged_preset(filament_json, "filament", bundled, tmp_dir)
            proc = _run_cli(slicer_bin, stls, out, machine, process_json, filament_json, arrange)
            try:
                if proc.returncode != 0:
                    raise SliceError(
                        f"exit={proc.returncode}\nstdout tail: {proc.stdout[-600:]}\n"
                        f"stderr tail: {proc.stderr[-600:]}"
                    )
                size = _validate_gcode_3mf(out)
                print(f"[slice] OK with {tag}: {out.name} (plate_1.gcode {size} bytes)")
                return out
            except SliceError as e:
                errors.append(f"--- attempt '{tag}' failed: {e}")
                out.unlink(missing_ok=True)
            # died with a signal (e.g. the macOS SIGSEGV bug) -> binary is unusable
            if proc.returncode < 0 or proc.returncode == 139:
                errors.append(f"    ({slicer_bin.name} crashed with a signal; skipping it)")
                break

    raise SliceError("all slicing attempts failed:\n" + "\n".join(errors))
