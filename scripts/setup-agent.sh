#!/usr/bin/env bash
# Recreate the Python env for the 3D Print Agent (agent/ package).
# System Python 3.14 has no wheels for the CAD/OCCT stack -> pin 3.12 via uv.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v uv >/dev/null || { echo "uv not found — install from https://docs.astral.sh/uv/"; exit 1; }

uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python \
    build123d trimesh manifold3d numpy networkx python-dotenv shapely pytest \
    pyvista pillow  # stage 6 verify: offscreen render (VTK) + PNG checks

# Headless slicing needs a working slicer CLI. Bambu Studio's CLI currently
# SEGFAULTs headless on macOS arm64 (bambulab/BambuStudio#8569); OrcaSlicer's
# CLI (same args, same bundled BBL A1 / PETG HF profiles) works and is used as
# the automatic fallback by agent/slice.py.
if [ ! -d /Applications/OrcaSlicer.app ]; then
  echo "NOTE: OrcaSlicer not found. If BambuStudio CLI segfaults, install it:"
  echo "      brew install --cask orcaslicer"
fi

echo
echo "OK. Run the pipeline with:"
echo "  .venv/bin/python -m agent.pipeline gear"
echo "  .venv/bin/python -m agent.pipeline gear --count 6"
echo "  .venv/bin/python -m pytest tests/agent -v"
