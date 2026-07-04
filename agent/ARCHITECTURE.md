# 3D Print Agent — архитектура реализации

Реализация плана `PLAN-3D-AGENT.md` (§8). Новый агент — **Python-пакет `agent/`**, запуск
**по требованию** (без демона). «Мозг» (understand / clarify / vision self-check) — сама
Claude-сессия (Claude Agent SDK / Claude Code), которая вызывает детерминированные модули ниже
как инструменты. Существующий Node/Express web-визард (`server/`, `web/`) — **legacy**, не трогаем.

## Стек и окружение
- Python **3.12** в изолированном venv через `uv` (в системе 3.14 — колёс под CAD/OCCT ещё нет).
- Слайсер: `/Applications/BambuStudio.app/Contents/MacOS/BambuStudio` (CLI) — установлен.
- Секреты — в `.env` (см. `.env.example`): `A1_IP`, `A1_SERIAL`, `A1_ACCESS_CODE`,
  `BAMBU_STUDIO_BIN`, `MESHY_API_KEY`.

## Дерево пакета
```
agent/
  config.py            # загрузка .env + путей + профилей; авто-детект слайсера
  spec.py              # BuildSpec: список объектов, размеры, mechanical/organic, part_count, допуски
  intake.py            # текст/голос/фото -> BuildSpec (schema + промпт; заполняет мозг)
  clarify.py           # пересказ + вопросы; блок до подтверждения
  generate/
    router.py          # маршрут объекта: precise->cad / organic->mesh
    cad.py             # CadQuery/build123d генераторы; spur_gear(); ОДИН STL НА ОБЪЕКТ
    mesh.py            # Meshy text/image-to-3D API (нужен MESHY_API_KEY)
  printability.py      # trimesh+manifold3d: watertight/winding, авторемонт, split слипшихся тел
  render.py            # offscreen-рендер каждого STL с нескольких ракурсов -> PNG
  verify.py            # рубрика ≥95%: bbox-замер vs спека + слоты для зрительной оценки
  slice.py             # обёртка Bambu Studio CLI + --arrange 1; грузит profiles/*.json
  printer.py           # bambulabs-api / MQTT+FTPS: ping, upload, start; видимость в Handy
  pipeline.py          # оркестратор стадий (то, что дёргает Claude-сессия) + CLI
  profiles/
    A1_machine.json    # экспорт из рабочего GUI-конфига (см. §Fragility плана)
    PETG_HF_process.json
    PETG_HF_filament.json
triggers/
  raycast/             # script command (хоткей -> поле -> сессия)
  shortcuts/           # iPhone Action Button + Run Script Over SSH (README)
tests/agent/           # pytest: gear, printability, slice-smoke
```

Модульная таблица 1:1 из `blueprint/agent-architecture.md`. Профили — из
`blueprint/petg-hf-slicer-profile.md` (§оверрайды процесса/филамента).

## Ключевые интерфейсы (пиннем, чтобы стадии стыковались)
```python
# spec.py
@dataclass
class ObjectSpec:
    name: str
    kind: Literal["mechanical", "organic"]
    dims_mm: dict          # напр. {"outer_d": 20, "thickness": 5, "teeth": 20, "module": 0.8, "bore": 5}
    count: int = 1
    tolerances_mm: float = 0.2
    notes: str = ""

@dataclass
class BuildSpec:
    objects: list[ObjectSpec]
    source_request: str
    reference_images: list[str] = field(default_factory=list)

# generate/cad.py  -> путь к STL (один объект)
def spur_gear(out: Path, *, teeth: int, module: float, thickness: float, bore: float) -> Path: ...
def generate_object(obj: ObjectSpec, out_dir: Path) -> list[Path]:  # count>1 -> N файлов

# printability.py
@dataclass
class GateResult:
    ok: bool; watertight: bool; winding_consistent: bool
    repaired: bool; split_into: list[Path]; report: str
def check_and_repair(stl: Path, out_dir: Path) -> GateResult: ...

# slice.py  -> .gcode.3mf (zip с Metadata/plate_1.gcode)
def slice_objects(stls: list[Path], out: Path, *, arrange: bool = True) -> Path: ...

# printer.py
def ping(cfg) -> bool
def upload(cfg, gcode_3mf: Path) -> str        # путь на устройстве
def start_print(cfg, device_path: str) -> None # видно в Bambu Handy
```

## Приёмочные критерии (из §9 — тестировать)
1. N объектов на плите РАЗДЕЛЬНО с верными размерами (напр. «6 шестерён» → 6 STL → 6 объектов).
2. Само-чек ≥95% реально гоняется и репортится.
3. Clarify блокирует до подтверждения.
4. Слайсинг всегда применяет профиль PETG HF (ironing ON).
5. Запуск on-demand с Raycast-хоткея и iPhone Action Button.
6. Нарезанное задание видно в Bambu Handy для финального Print.

## Статус стадий (§8) — журнал
- [x] 1. Скелет пакета `agent/` + `uv`-окружение (Python 3.12, build123d/trimesh/manifold3d) + config
- [x] 2. Триггеры (Raycast + iPhone Shortcut) — `bin/print-agent` + `triggers/raycast/` + `triggers/shortcuts/` (мозг-шов = стадия 3)
- [x] 3. intake + clarify — `intake.parse_request` + `clarify` (restate/questions/блок) + `pipeline` (`parse`/`spec`/`run`/`ping`); мозг-шов `bin/print-agent` (TTY→Claude, headless→pipeline)
- [x] 4a. generate: cad (`spur_gear` — настоящая эвольвента, Ø20 = (z+2)·m, z=20, m=20/22)
- [ ] 4b. generate: mesh (Meshy)
- [x] 5. printability gate (trimesh+manifold3d: watertight/winding, авторемонт, split тел)
- [x] 6. verify (vision ≥95%) — детерминированная половина: `render.py` (offscreen
  **pyvista/VTK**, проверено headless на arm64; PNG с 4 ракурсов, assert non-blank) +
  `verify.py` (bbox-замер, deviation vs спека, рубрика 35/25/20/15/5 — визуальные слоты
  `geometry`/`features` = null, их заполняет мозг по PNG) + `pipeline verify <spec.json>`
  (generate → gate → render → рубрика-JSON на stdout; БЕЗ слайсинга — verify идёт до него)
- [x] 7. slice → `.gcode.3mf` c PETG HF-оверрайдами (ironing ON, layer 0.16, сопло 252)
- [x] 8. printer handoff (FTP/MQTT) — `printer.py`: чистые билдеры payload'ов
  (project_file/pushall/stop/pause/resume/gcode_line — 1:1 к cheatsheet, покрыты
  оффлайн-pytest) + guarded-сеть (`ping` TCP:8883 никогда не кидает; `upload`
  implicit FTPS:990 через **bambulabs-api** с fallback на свой `ImplicitFTP_TLS`;
  `start_print` MQTT:8883; `handoff` = upload→start). CLI: `pipeline ping`
  (exit 0 всегда) и `pipeline send <f.gcode.3mf>` (без конфига — подсказка про
  .env, exit 0). **Код готов, e2e против живого A1 не гонялся** (стадия 9).
- [ ] 9. e2e: шестерня Ø20 мм + фигурка

**Первый срез (готов):** stage 1 + 4a + 5 + 7 — `python -m agent.pipeline gear [--count 6]`
проходит шестерня Ø20 → gate → slice локально; 6 шестерён = 6 раздельных объектов на плите.

**Грабля слайсера (2026-07):** Bambu Studio 02.05.00.66 CLI на macOS arm64 headless
падает SIGSEGV до слайсинга (upstream #8569/#3453 — `wxGetApp().plater()` по null
`wxTheApp` в `PartPlateList::generate_print_polygon`; флагами не обходится).
`agent/slice.py` пробует Bambu Studio, при крэше автоматически уходит на
**OrcaSlicer 2.4.1** (`brew install --cask orcaslicer`) — тот же CLI, те же
бандловые BBL-профили A1/PETG HF, наши override-JSON (`agent/profiles/`,
через `inherits`) грузятся и применяются.
