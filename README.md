# 🖨️ 3D Print Agent — Bambu Lab A1

Describe a part in plain language — get a printable, sliced job.

The agent asks what it got right, generates real CAD geometry (**one STL per object**, never a
fused blob), gates it for printability, **looks at its own renders** to score them against your
request, and slices with a tuned PETG HF profile.

> 📖 **Installing this on your machine? Read [SETUP.md](SETUP.md)** — step-by-step setup,
> requirements, printer configuration and troubleshooting (in Russian).

```bash
bin/print-agent "напечатай 6 шестерён Ø20мм, module 1, толщина 5, отверстие 5"
# → clarifying questions → 6 separate STLs → printability gate → self-check → .gcode.3mf
```

---

## How it works: brain and hands

The agent is deliberately split in two:

| Layer | Runs as | Where |
|---|---|---|
| **Brain** — understanding, clarification, vision self-check | a **Claude Code session** | prompt in `agent/BRAIN.md` |
| **Hands** — CAD, printability gate, render, slice, printer I/O | a **Python package**, called as tools | `agent/` |

The brain reasons; the hands are deterministic and unit-tested. `bin/print-agent` opens a Claude
Code session in this repo, hands it your request, and the session drives `agent/pipeline.py`
through Bash.

**Consequence:** without a Claude Code subscription you still get the deterministic half
(`python -m agent.pipeline gear`), but not the conversational "describe it in words" flow.

---

## Pipeline

```
request (text + optional photo/voice)
   │
   1. UNDERSTAND    brain reads text/photo → structured BuildSpec
   2. CLARIFY       restates, asks questions — BLOCKS until you confirm
   3. GENERATE      code-CAD (build123d/OCCT) → ONE STL PER OBJECT
   4. GATE          trimesh + manifold3d: watertight, winding, auto-repair, split fused bodies
   5. SELF-CHECK    offscreen renders (pyvista) → rubric; brain scores geometry by sight, ≥95%
   6. SLICE         OrcaSlicer CLI + PETG HF profile (ironing ON), --arrange 1
   7. HANDOFF       FTPS upload + MQTT start → job appears in Bambu Handy
   │
   ▼
.gcode.3mf — you press Print
```

---

## Requirements

macOS · [Claude Code](https://claude.com/claude-code) · `uv` · Python **3.12** (not 3.14 — no
OCCT wheels) · OrcaSlicer · Bambu Lab A1 on 2.4 GHz Wi-Fi · Bambu PETG HF filament.

```bash
git clone https://github.com/Ianromanenko/3d-print-agent.git
cd 3d-print-agent
bash scripts/setup-agent.sh
.venv/bin/python -m agent.pipeline gear --count 6   # verify: 6 separate gears in output/
```

Full instructions — **[SETUP.md](SETUP.md)**.

---

## CLI

```bash
python -m agent.pipeline parse "6 gears Ø20"   # heuristic BuildSpec draft (brain corrects it)
python -m agent.pipeline spec spec.json        # generate → gate → slice
python -m agent.pipeline verify spec.json      # generate → gate → render → rubric JSON
python -m agent.pipeline gear --count 6        # demo path, no printer needed
python -m agent.pipeline ping                  # printer reachability (never blocks, exit 0)
python -m agent.pipeline send out.gcode.3mf    # FTPS upload + MQTT start
```

---

## Status

| Stage | |
|---|---|
| Package skeleton, env, config | ✅ |
| Triggers (Raycast hotkey, iPhone Action Button) | ✅ |
| Understand + blocking clarify | ✅ |
| CAD generation (mechanical, involute gears) | ✅ |
| **Organic/figurine generation (Meshy)** | ❌ not implemented |
| Printability gate | ✅ |
| Self-check ≥95% (render + rubric) | ✅ |
| Slicing with PETG HF profile | ✅ |
| Printer handoff (FTPS + MQTT) | ⚠️ code done, **never run against a live printer** |
| End-to-end test on a real A1 | ❌ not run |

**Ask it for mechanical parts** — gears, brackets, dimensioned things. Organic shapes aren't
supported yet and the agent will say so rather than fake it.

### Known upstream issue

Bambu Studio 02.05.00.66's CLI segfaults headless on macOS arm64
([#8569](https://github.com/bambulab/BambuStudio/issues/8569) — null `wxTheApp` deref).
`agent/slice.py` detects the crash and falls back to OrcaSlicer, which ships the same CLI and
the same bundled BBL A1 / PETG HF profiles. This is expected behaviour, not a bug to fix.

---

## Layout

```
agent/           Python package — the "hands"
  BRAIN.md       prompt the Claude session follows
  pipeline.py    orchestrator + CLI (what the brain calls)
  generate/cad.py, printability.py, render.py, verify.py, slice.py, printer.py
  profiles/      PETG HF slicer overrides (ironing, temps, layer height)
knowledge/       printer, parameters (symptom→cause→fix), ironing, filaments, PETG HF plan
blueprint/       architecture, exact slicer JSON overrides, printer-control cheatsheet
triggers/        Raycast script command · iPhone Shortcut over SSH
tests/agent/     pytest — CAD, gate, verify, printer payloads (offline)
PLAN-3D-AGENT.md full original plan and rationale

server/, web/    ⚠️ legacy Phase-1 Node wizard — superseded, kept for reference, not maintained
```

---

## License

MIT — see [LICENSE](LICENSE)
