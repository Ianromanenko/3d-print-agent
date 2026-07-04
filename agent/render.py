"""Offscreen STL rendering for the vision self-check (stage 6, BRAIN.md step 5).

Backend: **pyvista/VTK** — verified empirically to render offscreen on this Mac
(macOS arm64, Python 3.12) without a window server: `Plotter(off_screen=True)`
produces shaded, recognizable multi-angle PNGs. (trimesh's own viewer needs a GL
window and does NOT work headless; matplotlib `mplot3d` on the Agg backend is
the documented fallback if VTK offscreen ever breaks here.)

Every PNG is asserted non-blank (pixel variance) before being returned — a
blank render would silently poison the visual scoring.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

# (view name, pyvista camera_position, extra azimuth degrees)
_BASE_VIEWS: list[tuple[str, str, float]] = [
    ("iso", "iso", 0.0),
    ("front", "xz", 0.0),
    ("top", "xy", 0.0),
    ("side", "yz", 0.0),
]

_WINDOW_SIZE = (800, 600)
_MESH_COLOR = "#c8d2e0"  # light steel — shades legibly on the dark background
_BACKGROUND = "#202430"
_MIN_PIXEL_STD = 1.0  # below this the image is effectively one flat color


def _views(n: int) -> list[tuple[str, str, float]]:
    """First n views: the 4 canonical ones, then extra rotated isometrics."""
    views = list(_BASE_VIEWS[:n])
    deg = 0.0
    while len(views) < n:
        deg += 45.0
        views.append((f"iso{int(deg)}", "iso", deg))
    return views


def render_object(stl: Path, out_dir: Path, n_views: int = 4) -> list[Path]:
    """Render `stl` from `n_views` distinct camera angles into `out_dir`.

    Writes `<stem>_<view>.png` per view (object centered, fully in frame,
    consistent light-kit lighting) and returns the paths. Raises RuntimeError
    if any render comes out blank.
    """
    stl = Path(stl)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if n_views < 1:
        raise ValueError(f"n_views must be >= 1, got {n_views}")

    mesh = pv.read(str(stl))
    paths: list[Path] = []
    pl = pv.Plotter(off_screen=True, window_size=list(_WINDOW_SIZE))
    try:
        pl.set_background(_BACKGROUND)
        pl.add_mesh(mesh, color=_MESH_COLOR, smooth_shading=True, specular=0.3)
        for name, cpos, azimuth in _views(n_views):
            pl.camera_position = cpos
            pl.reset_camera()  # center the object and fit it fully in frame
            if azimuth:
                pl.camera.azimuth(azimuth)
            out = out_dir / f"{stl.stem}_{name}.png"
            img = pl.screenshot(str(out), return_img=True)
            std = float(np.asarray(img).std())
            if not out.is_file() or out.stat().st_size == 0 or std < _MIN_PIXEL_STD:
                raise RuntimeError(
                    f"blank render for {stl.name} view '{name}' "
                    f"(size={out.stat().st_size if out.is_file() else 0}B, pixel std={std:.3f})"
                )
            paths.append(out)
    finally:
        pl.close()
    return paths
