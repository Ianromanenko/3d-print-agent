"""Configuration: .env loading, path resolution, slicer auto-detection."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = REPO_ROOT / "agent"
PROFILES_DIR = AGENT_DIR / "profiles"
OUTPUT_DIR = REPO_ROOT / "output"

# Default locations for slicer CLI binaries, in probe order.
# Bambu Studio is the pinned slicer (PLAN §4), but its CLI segfaults headless on
# macOS arm64 (upstream bugs #8569/#3453: null wxTheApp deref in
# PartPlateList::generate_print_polygon). OrcaSlicer — same CLI, same bundled
# BBL A1 + PETG HF system profiles, no such bug — is the working fallback.
_SLICER_CANDIDATES = [
    "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
    "/Applications/Bambu Studio.app/Contents/MacOS/BambuStudio",
    "/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer",
]

# Bundled system profiles that ship inside Bambu Studio (most reliable for the CLI).
BUNDLED_PROFILE_NAMES = {
    "machine": "Bambu Lab A1 0.4 nozzle",
    "process": "0.20mm Standard @BBL A1",
    "filament": "Bambu PETG HF @BBL A1",
}


@dataclass
class Config:
    """Resolved runtime configuration for the pipeline."""

    slicer_bin: Path
    slicer_bins: list[Path] = field(default_factory=list)  # all candidates, in try order
    profiles_dir: Path = PROFILES_DIR
    output_dir: Path = OUTPUT_DIR
    # Printer (stage 8; unused in the first slice but loaded for completeness)
    a1_ip: str = ""
    a1_serial: str = ""
    a1_access_code: str = ""
    meshy_api_key: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def bundled_profiles_dir(self) -> Path:
        """<SlicerApp>/Contents/Resources/profiles/BBL (same layout in Studio and Orca)."""
        return bundled_profiles_dir(self.slicer_bin)

    def bundled_profile(self, kind: str, name: str | None = None) -> Path:
        """Path to a bundled system profile JSON (kind: machine|process|filament)."""
        name = name or BUNDLED_PROFILE_NAMES[kind]
        return self.bundled_profiles_dir / kind / f"{name}.json"


def printer_configured(cfg: Config) -> bool:
    """True when all three A1 fields are set in .env (stage-8 handoff possible)."""
    return bool(cfg.a1_ip and cfg.a1_serial and cfg.a1_access_code)


def bundled_profiles_dir(slicer_bin: Path) -> Path:
    return Path(slicer_bin).parent.parent / "Resources" / "profiles" / "BBL"


def detect_slicers() -> list[Path]:
    """Locate slicer CLI binaries, best-first (BAMBU_STUDIO_BIN override wins)."""
    found: list[Path] = []
    env_bin = os.environ.get("BAMBU_STUDIO_BIN", "").strip()
    if env_bin:
        p = Path(env_bin)
        if not p.is_file():
            raise FileNotFoundError(f"BAMBU_STUDIO_BIN points to a missing file: {p}")
        found.append(p)
    for cand in _SLICER_CANDIDATES:
        p = Path(cand)
        if p.is_file() and p not in found:
            found.append(p)
    for name in ("bambu-studio", "BambuStudio", "orca-slicer"):
        w = shutil.which(name)
        if w and Path(w) not in found:
            found.append(Path(w))
    if not found:
        raise FileNotFoundError(
            "No slicer CLI found. Install Bambu Studio (or OrcaSlicer), "
            "or set BAMBU_STUDIO_BIN in .env"
        )
    return found


def load_config(env_file: Path | None = None) -> Config:
    """Load .env (repo root by default) and resolve everything."""
    load_dotenv(env_file or REPO_ROOT / ".env")
    slicers = detect_slicers()
    cfg = Config(
        slicer_bin=slicers[0],
        slicer_bins=slicers,
        a1_ip=os.environ.get("A1_IP", ""),
        a1_serial=os.environ.get("A1_SERIAL", ""),
        a1_access_code=os.environ.get("A1_ACCESS_CODE", ""),
        meshy_api_key=os.environ.get("MESHY_API_KEY", ""),
    )
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    return cfg
