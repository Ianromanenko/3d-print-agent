# 3D Print Agent — Design Spec

**Date:** 2026-05-03
**Status:** Draft (awaiting user review)
**Owner:** Yan Romanenko (@ianromanenko)

---

## 1. Problem & Vision

A first-time 3D-printer owner (Bambu Lab A1, Bambu PLA Silk White) needs an agent that walks them through everything from physical setup to a successful first print, with illustrated step-by-step instructions, a 3D model viewer, model discovery on MakerWorld, and built-in troubleshooting.

The agent must be **extensible** so future iterations can add: AI text-to-3D generation, alternative slicers, additional model sources, and other printers.

---

## 2. Goals

- A guided wizard that takes a beginner from unboxing to a successful print.
- Visual instructions for every physical step (Bambu official photos where allowed; illustrated SVG fallback).
- 3D model viewer with rotation, zoom, dimensions.
- MakerWorld search + local file upload.
- Troubleshooting flows accessible from any step.
- Architecture ready to support future features (AI generation, new adapters) without rewrites.

## 3. Non-Goals (for now)

- Multi-printer support, print farms, multi-user.
- Filament inventory tracking.
- Mobile app (architecture must allow it later, but no implementation).

---

## 4. Architecture

### 4.1 High-level

```
Browser (Claude Preview MCP / any browser)
  ─ Wizard UI (HTML + vanilla JS, modular)
  ─ 3D viewer (Three.js)
       │ HTTP + WebSocket  (localhost:3030)
       ▼
Node.js Backend (Express + ws)
  ─ Versioned API  (/api/v1/...)
  ─ Service Layer  (interfaces)
  ─ Adapter Layer  (swappable implementations)
       │ subprocess / HTTPS
       ▼
External tools (OrcaSlicer CLI → Bambu Cloud → A1)
```

### 4.2 Layers

| Layer | Purpose | Examples |
|---|---|---|
| **API** | Versioned HTTP/WS contract for the frontend | `/api/v1/search`, `/api/v1/print` |
| **Services** | Interfaces declaring *what* an operation does | `ModelSource`, `Slicer`, `PrinterDriver`, `ModelGenerator` |
| **Adapters** | Concrete implementations of each service | `makerworld.js`, `orcaslicer.js`, `bambu-cloud.js` |
| **External** | Tools/APIs the adapters wrap | OrcaSlicer CLI, MakerWorld web, Bambu Cloud MQTT |

### 4.3 Extensibility

| Future feature | Plugs in as |
|---|---|
| AI text-to-3D generation | New `ModelGenerator` adapter (e.g. `openai-3d.js`) |
| Different slicer (PrusaSlicer) | New `Slicer` adapter |
| Non-Bambu printer | New `PrinterDriver` adapter |
| Additional marketplace (Thingiverse, Printables) | New `ModelSource` adapter |
| Auto-orientation / model repair | New service in service layer |
| User accounts / cloud sync | New service + DB layer (no UI rewrite) |
| Mobile companion | Same versioned API, new frontend |

### 4.4 Why this works
- Frontend depends only on the **versioned API**; backend internals can change freely.
- Services define *what*, adapters define *how* → swap implementations with a config change.
- WebSocket channel for live updates (print progress) is in place from day 1, even if Phase 1 only uses it for mocked status.

---

## 5. Wizard Flow

The wizard is a linear sequence with persistent state. Users can go back, skip optional steps, and access the help/troubleshooting panel at any time.

### Stage 1 — One-time hardware setup *(skipped on subsequent prints)*

| # | Step | Action | Visual aid |
|---|---|---|---|
| 1.1 | Welcome | Read intro, click "Start" | Hero image of A1 |
| 1.2 | Unbox check | Confirm parts present | Checklist + photos |
| 1.3 | Place printer | Stable surface, 10 cm clearance | Diagram |
| 1.4 | Power on | Flip switch on back | Photo of switch |
| 1.5 | Initial calibration | Press OK on printer screen | Photo of screen |
| 1.6 | Connect to WiFi | Use printer touchscreen | Screenshots |
| 1.7 | Bind to Bambu account | Scan QR with Bambu Handy app | Photo of QR |
| 1.8 | Install OrcaSlicer | Download + install | Installer screenshots |
| 1.9 | First-launch login | Sign in with Bambu account | Screenshots |
| 1.10 | Verify connection | Backend pings printer | Live status indicator |

### Stage 2 — Per-print setup *(every print)*

| # | Step | Action |
|---|---|---|
| 2.1 | Clean build plate | Wipe with 90 %+ isopropyl alcohol (animated GIF) |
| 2.2 | Load filament | Insert PLA Silk White (path diagram) |
| 2.3 | Confirm filament type | Dropdown defaults to "Bambu PLA Silk White" |

### Stage 3 — Choose what to print

| # | Step |
|---|---|
| 3.1 | Describe in text *or* paste MakerWorld URL *or* upload STL/3MF |
| 3.2 | (If text) See 3-5 result cards with thumbnails, sizes, ratings |
| 3.3 | Pick model |

### Stage 4 — Preview & confirm

| # | Step |
|---|---|
| 4.1 | 3D viewer: rotate, zoom, pan, dimensions in mm, est. print time/filament |
| 4.2 | Adjust scale, orientation, copies (optional) |
| 4.3 | Slice (Phase 2: real OrcaSlicer; Phase 1: mocked) |
| 4.4 | Big "Send to printer" button |

### Stage 5 — Printing

| # | Step |
|---|---|
| 5.1 | Sending job → printer received |
| 5.2 | Live monitor over WebSocket (Phase 2) |
| 5.3 | Pause/cancel controls (Phase 2) |
| 5.4 | Done — removal instructions |

### Stage 6 — Troubleshooting (always accessible)

Side panel categorized by symptom:
- Printer not detected
- First-layer adhesion
- Stringing / blobs
- Filament jam
- Print stopped mid-way
- Software errors

Each issue: symptom → likely cause → step-by-step fix with images.

### State model
- Persisted in `localStorage`; refresh-safe.
- `setupComplete` flag → Stage 1 auto-skipped on later prints, with a "redo setup" link.
- Each step: `not-started | in-progress | completed | skipped`.

---

## 6. File / Folder Structure

```
3d-print-agent/
├── README.md
├── LICENSE                      (MIT)
├── .gitignore
├── package.json
├── config.json                  (which adapters, ports)
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── adding-an-adapter.md
│   ├── superpowers/specs/...
│   └── images/
│
├── server/
│   ├── index.js
│   ├── config.js
│   ├── api/v1/
│   │   ├── index.js
│   │   ├── search.js
│   │   ├── download.js
│   │   ├── slice.js
│   │   ├── print.js
│   │   ├── status.js
│   │   └── wizard.js
│   ├── services/
│   │   ├── ModelSource.js
│   │   ├── Slicer.js
│   │   ├── PrinterDriver.js
│   │   ├── ModelGenerator.js
│   │   └── registry.js
│   ├── adapters/
│   │   ├── model-sources/{makerworld.js, local-upload.js, thingiverse.js[stub]}
│   │   ├── slicers/orcaslicer.js              (Phase 2)
│   │   ├── printer-drivers/bambu-cloud.js     (Phase 2)
│   │   └── model-generators/                  (future)
│   ├── websocket/print-status.js
│   └── lib/{logger.js, errors.js, file-store.js}
│
├── web/
│   ├── index.html
│   ├── style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── api-client.js
│   │   ├── state.js
│   │   ├── router.js
│   │   ├── i18n.js                            (EN now, structured for UA later)
│   │   ├── steps/{1.1-welcome.js, ..., step-base.js}
│   │   ├── components/{viewer-3d.js, image-step.js, help-panel.js, progress-bar.js}
│   │   └── vendor/three.min.js
│   └── assets/
│       ├── images/                            (official Bambu photos where allowed)
│       ├── illustrations/                     (generated SVG fallback)
│       └── troubleshooting/
│
├── data/
│   ├── models/                                (gitignored, downloaded STL/3MF cache)
│   ├── slices/                                (gitignored, G-code cache)
│   └── wizard-state.json                      (gitignored, server-side backup)
│
├── scripts/{check-orcaslicer.sh, dev.sh}
└── tests/{adapters/, services/}
```

### gitignored
`node_modules/`, `data/models/`, `data/slices/`, `data/wizard-state.json`, `.env`, `.DS_Store`, IDE configs.

### config.json shape
```json
{
  "port": 3030,
  "services": {
    "modelSource": "makerworld",
    "slicer": "orcaslicer",
    "printerDriver": "bambu-cloud"
  },
  "orcaslicer": { "executablePath": "auto-detect" }
}
```

---

## 7. Phase 1 Scope

### In scope (build now)
- Express server on `localhost:3030` with versioned API and stub routes for unbuilt features.
- Service registry + adapter pattern wired up.
- Adapters built: `local-upload`, `makerworld`.
- Frontend wizard: all Stage 1 + Stage 2 steps with illustrated instructions, Stage 3 (search + upload), Stage 4 (3D viewer + dimensions), Stage 5 (mocked progress), help panel with 3-4 troubleshooting flows.
- 3D viewer: STL + 3MF, orbit controls, bounding-box dimensions in mm, wireframe toggle, lighting, ground plane, reset view.
- Wizard infrastructure: step navigation, `localStorage` persistence, setup-complete flag, help panel.
- ~10-15 generated SVG illustrations (style chosen after sample review).
- GitHub repo created, MIT-licensed, README with setup + screenshots, conventional-commit messages, tagged `v0.1.0` at end of Phase 1.
- Tests as we go: backend services + adapters; frontend smoke tests where reasonable.

### Deferred to Phase 2
- `orcaslicer.js` (real slicing) and `bambu-cloud.js` (real printing) adapters.
- WebSocket live print status; pause/cancel controls.
- Bambu account auth/credential storage in `.env`.
- Camera feed integration.

### Deferred to Phase 3+
- AI text-to-3D model generation.
- Additional marketplaces (Thingiverse, Printables).
- Auto-orientation / model repair.
- User accounts, cloud sync, mobile companion.

### Phase 1 success criteria
1. `npm install && npm start` works; `localhost:3030` opens the wizard.
2. Full onboarding wizard clickable end-to-end with illustrated steps.
3. MakerWorld search returns results for a real query.
4. Pick a result → renders in 3D, rotates, shows dimensions.
5. Local STL/3MF upload works.
6. Click "Send to printer" → mocked progress UI completes.
7. Refresh preserves wizard progress.
8. Troubleshooting flow accessible from any step.
9. GitHub repo public, MIT-licensed, clean conventional-commit history, tagged `v0.1.0`.

---

## 8. Decisions Made (from brainstorm)

| # | Decision | Choice |
|---|---|---|
| 1 | Repo visibility | Public |
| 2 | Project location | `~/Projects/3d-print-agent` |
| 3 | License | MIT |
| 4 | Bambu credentials storage | `.env` file (gitignored), Phase 2 only |
| 5 | Wizard language | English now, code structured for i18n |
| 6 | Image style | TBD — generate samples of (line-art / cartoon / schematic) for user to pick before committing |
| 7 | Testing | Tests as we go |
| 8 | GitHub username | `ianromanenko` |
| 9 | GitHub CLI | Install `gh` via Homebrew |

---

## 9. Build Sequence (rough order)

1. Repo init + GitHub push (`v0.0.1`).
2. Project scaffold + `npm install` working — `chore: scaffold`.
3. Backend skeleton + stub routes — `feat: backend skeleton`.
4. Wizard infrastructure (router, state, base step) — `feat: wizard core`.
5. Generate 3 image-style samples → user picks → commit chosen style guide.
6. First few illustrated steps to validate the look — `feat: setup steps 1.1-1.5`.
7. Remaining setup steps — `feat: complete setup wizard`.
8. 3D viewer component — `feat: 3d viewer`.
9. Local upload adapter + viewer integration — `feat: local upload`.
10. MakerWorld adapter — `feat(adapter): makerworld search`.
11. Mocked print stage + help panel — `feat: print stage mock + help`.
12. Polish + README + screenshots — `docs: readme + tag v0.1.0`.

---

## 10. Risks & Open Items

- **MakerWorld API access** — no public/documented API. May need scraping or undocumented endpoints; could break. Mitigation: `local-upload` adapter exists from day 1 as fallback.
- **OrcaSlicer CLI documentation** — sparse. May need experimentation in Phase 2.
- **Bambu Cloud auth** — not addressed in Phase 1. Will need investigation in Phase 2.
- **Image sourcing** — official Bambu photos may have license constraints. Default to generated SVG illustrations; only use Bambu photos with verified permission.
- **Three.js 3MF loader** — `3MFLoader` exists in three.js examples but is less polished than `STLLoader`. Need to test early.

---

## 11. After This Spec

1. Self-review of this document.
2. User reviews this spec.
3. On approval → invoke `superpowers:writing-plans` to produce step-by-step implementation plan.
4. Implementation begins.
