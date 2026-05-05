# 🖨️ 3D Print Agent

An AI-guided 3D printing assistant for the **Bambu Lab A1** — built for beginners.

Step-by-step illustrated wizard from unboxing to a finished print, with a live 3D model viewer, MakerWorld search, and built-in troubleshooting.

---

## Features (Phase 1)

- **Guided wizard** — hardware setup, filament loading, every physical step with illustrated SVG instructions
- **MakerWorld search** — find models by description, see thumbnails and ratings
- **Local file upload** — drag and drop your own STL or 3MF
- **3D model viewer** — rotate, zoom, pan, see dimensions in mm (Three.js)
- **Mocked print flow** — full UI end-to-end including a progress simulation
- **Troubleshooting panel** — 6 common issue flows, accessible from any step
- **Persistent state** — refresh-safe wizard progress via localStorage
- **Extensible architecture** — service/adapter pattern; swap slicers, sources, printers via config

## Coming in Phase 2

- Real OrcaSlicer CLI integration (slicing + printing)
- Bambu Cloud MQTT connection (live print status)
- Pause/cancel controls
- Camera feed

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/Ianromanenko/3d-print-agent.git
cd 3d-print-agent

# 2. Install
npm install

# 3. Start
npm start
# → http://localhost:3030
```

> **Node.js 20+** required.

---

## Resuming development

If you're picking this up after a break:

```bash
git log --oneline      # see what was last committed
cat docs/superpowers/specs/2026-05-03-3d-print-agent-design.md  # full architecture
npm start              # verify it still runs
```

---

## Architecture

```
Browser (localhost:3030)
  └─ Wizard UI (vanilla JS ES modules, Three.js)
       │ HTTP + WebSocket
       ▼
Express server (Node.js)
  ├─ /api/v1/  — versioned REST API
  ├─ Services  — ModelSource, Slicer, PrinterDriver, ModelGenerator
  └─ Adapters  — makerworld, local-upload, orcaslicer(stub), bambu-cloud(stub)
       │
       ▼
External: OrcaSlicer CLI → Bambu Cloud → A1
```

Swap any adapter by changing one line in `config.json`.  
See `docs/adding-an-adapter.md` (coming soon) for the pattern.

---

## Config

`config.json` — controls which adapter each service uses:

```json
{
  "port": 3030,
  "services": {
    "modelSource": "makerworld",
    "slicer": "orcaslicer",
    "printerDriver": "bambu-cloud"
  }
}
```

---

## Project structure

```
server/
  api/v1/          Versioned HTTP routes
  services/        Interface definitions
  adapters/        Concrete implementations
  websocket/       Live print status (Phase 2)
  lib/             logger, errors, file-store

web/
  js/steps/        One file per wizard step
  js/components/   viewer-3d, help-panel, etc.
  assets/illustrations/  SVG instruction diagrams

tests/
  adapters/        Adapter unit tests
  services/        Registry + service tests
```

---

## License

MIT — see [LICENSE](LICENSE)
