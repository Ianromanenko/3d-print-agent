# ⭐ Мастер‑промпт для Fable 5

Открой **Fable 5** (или Opus 4.8) в папке проекта на Mac и вставь блок ниже целиком.
Он ссылается на `PLAN-3D-AGENT.md`, `knowledge/` и остальные файлы `blueprint/` в этом репозитории.

```
You are building a local "3D Print Agent" that runs on my Mac and drives my Bambu Lab A1.
Follow PLAN-3D-AGENT.md and the files in knowledge/ and blueprint/ in this repo.
Build it in the staged order in PLAN-3D-AGENT.md §8.

ENVIRONMENT (fixed):
- Backend runs on my Mac, on the same Wi‑Fi as the A1. Launch is ON‑DEMAND (no daemon):
  each trigger starts a fresh agent session.
- The A1 is (or will be) in LAN Mode + Developer Mode. Local control only:
  MQTT mqtts://<ip>:8883 (user bblp, pass = LAN access code, topics device/<serial>/request|report),
  and implicit‑FTPS upload on port 990. Prefer the `bambulabs-api` Python lib; fall back to raw MQTT/FTP.
  See blueprint/printer-control-cheatsheet.md for exact payloads.
- Filament in the machine: Bambu PETG HF White Matte. Always slice with the profile in
  knowledge/05-petg-hf-print-plan.md and blueprint/petg-hf-slicer-profile.md.
- Final handoff: upload the sliced .gcode.3mf so the job appears in Bambu Handy; I press Print there.

TRIGGERS (see blueprint/launch-setup.md):
- Primary (Mac): a Raycast script command bound to a hotkey. Takes typed text as an argument and
  opens an interactive agent session in the project with that request.
- Secondary (iPhone): an Apple Shortcut on the Action Button collecting text (Ask for Input/Dictate),
  audio (Record Audio), and photos (Take Photo/Select Photos), then "Run Script Over SSH" to start the
  same session on the Mac with the text/files attached. Clarifications via push; result appears in Handy.
- At session start, ping the A1 over MQTT and warn me if the printer is off/unreachable.

BRAIN:
- Use the smartest available model (Fable 5, else Opus 4.8) for intent parsing, CAD code authoring, and
  self‑check scoring. Spin up research subagents for "how to model X / what standard for Y".

PIPELINE (implement exactly):
1) UNDERSTAND: my text + transcribed audio + photos → a STRUCTURED build‑spec:
   object list, per‑object dimensions, mechanical‑vs‑organic, part count, tolerances, constraints.
2) CLARIFY: restate understanding + targeted questions. BLOCK until I confirm/correct. No modeling before that.
3) GENERATE (hybrid router):
   - precise/mechanical (gears, brackets, threaded, dimensioned) → CadQuery/build123d (OCCT) or
     OpenSCAD + BOSL2 for gears. ONE STL PER DISTINCT OBJECT, each individually dimensioned.
   - organic/figurine → Meshy text/image‑to‑3D API → mesh.
4) PRINTABILITY GATE: trimesh + manifold3d + pymeshlab — assert watertight AND winding‑consistent;
   auto‑repair; regenerate if unfixable. Split any merged scene into separate bodies.
5) SELF‑CHECK LOOP (>=95%): offscreen‑render each object from multiple angles; feed renders + my original
   request (+ reference photos) to the vision model; score geometry, proportions, feature completeness, and
   — for mechanical — PART COUNT, SEPARATENESS (not merged), MEASURED dimensions vs spec. If <95%, diagnose,
   edit CAD params / regenerate, re‑render, re‑score. Loop to threshold or a max‑iteration cap. Never hand me
   a part scored <95% without flagging it. Report the final confidence.
6) SLICE (headless): Bambu Studio CLI with the A1 machine profile + PETG HF filament profile + a process
   profile carrying the smooth+ironing overrides. Pass all STLs together with --arrange 1 so they lay out as
   SEPARATE objects on one plate. Output a .gcode.3mf (zip with Metadata/plate_1.gcode). Do per‑parameter
   control by EDITING the process/filament JSON, not undocumented CLI flags.
7) HANDOFF: FTP the .gcode.3mf to the A1 so it's startable from Bambu Handy; notify my phone
   "ready to review in Handy."

HARD REQUIREMENTS (acceptance criteria — test these):
- Multi‑object requests yield N SEPARATE objects with correct per‑object sizes (e.g. "6 gears" → 6 distinct
  STLs, 6 objects after slicing), never one fused model.
- The >=95% self‑check loop actually runs and is reported.
- The clarify step blocks until I confirm.
- Slicing always applies the PETG HF profile (incl. ironing on).
- Launches on‑demand from the Raycast hotkey and from the iPhone Action Button.
- The sliced job shows up in Bambu Handy for my final review + Print.

FRAGILITY TO HANDLE:
- Bambu firmware auth: rely on LAN Developer Mode; handle the printer's self‑signed TLS cert
  (don't verify/pin). Pin a validated Bambu Studio version.
- Bambu Studio CLI can fail to load external presets — export validated machine/process/filament JSONs
  from a working GUI config and load those.
- AI meshes are often non‑manifold — always run the printability gate; prefer code‑CAD for precise parts.
- iOS media quirks — use the Shortcut for intake and Bambu Handy for review.

FINAL STEP: run the end‑to‑end test — a 20mm spur gear (checks precision + separateness) and a simple
figurine (checks organic path) — and show me the results.
```
