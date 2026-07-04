# План создания 3D‑Print агента для Bambu Lab A1

> Отполированный, готовый к запуску план. Ты открываешь **Fable 5** (или Opus 4.8) в проекте на Mac,
> вставляешь мастер‑промпт из раздела **§9**, и модель строит агента по этому плану.
> Оборудование: **Bambu Lab A1** + **Bambu PETG HF White Matte**. Бэкенд — на **Mac** в одной Wi‑Fi‑сети с принтером.

---

## 1. Что мы строим (в двух абзацах)

Агент, которому ты на iPhone (кнопкой действия) или на Mac (хоткеем Raycast) даёшь **текст + опционально фото/голос** с описанием того, что надо напечатать. Агент **уточняет, правильно ли понял**, затем **генерирует настоящую печатаемую 3D‑модель** (если объектов несколько — например 6 шестерёнок — это 6 **отдельных** объектов на столе с правильными размерами, а не один монолит), **сам себя проверяет** по картинке против твоего запроса, пока не будет ≥95 % уверен, что совпадает, **нарезает** её слайсером с настройками под твой PETG HF и **кладёт готовое задание в Bambu Handy** — тебе остаётся покрутить модель, глянуть и нажать «Печать».

Тяжёлая часть (генерация, слайсинг, связь с принтером) живёт на **Mac**. iPhone — только триггер и экран проверки: он физически не может нарезать модель или управлять принтером. Запуск — **по требованию** (без постоянного демона): каждый триггер поднимает свежую сессию агента.

---

## 2. Подтверждённые решения

| Решение | Выбор |
|---|---|
| Хост бэкенда | **Mac** в одной сети с A1 |
| Генерация моделей | **Гибрид**: код‑CAD для точных/механических деталей + AI‑меш для органики/фигурок |
| Финальная выдача | Задание появляется в **Bambu Handy**, ты жмёшь «Печать» там |
| Модель запуска | **По требованию**, без демона |
| Триггер на Mac | **Raycast‑хоткей** → поле ввода → интерактивная сессия агента |
| Триггер на iPhone | **Кнопка действия** → Shortcut → `Run Script Over SSH` в Mac → та же сессия |
| «Мозг» агента | **Fable 5** (если доступен), иначе **Opus 4.8**; сабагенты для дип‑ресёрча |

---

## 3. Архитектура выполнения (пайплайн)

```
ТРИГГЕР (по требованию, без демона):
  • Mac:    Raycast‑хоткей → поле ввода → открывается интерактивная сессия Claude Code в проекте
  • iPhone: Кнопка действия → Shortcut (текст + голос + фото) → SSH в Mac → старт сессии
        │
        ▼
Сессия агента на Mac  (сначала пингует A1 по MQTT; предупреждает, если принтер выключен)
  1. ПОНИМАНИЕ  (умная модель, зрение) — распознать голос, прочитать фото,
     собрать структурную спеку: список объектов, размеры, механика/органика,
     кол‑во деталей, допуски, ограничения.
  2. УТОЧНЕНИЕ  — агент пересказывает, что понял, и задаёт точечные вопросы;
     отправляет их тебе; ЖДЁТ подтверждения/правок ДО моделирования.
  3. ГЕНЕРАЦИЯ (гибридный роутер):
       • точное/механика → код на CadQuery/build123d (OCCT) или OpenSCAD+BOSL2
         (шестерни). КАЖДЫЙ объект = отдельный STL со своими размерами.
       • органика/фигурка → Meshy text/image‑to‑3D API → меш.
  4. ВОРОТА ПЕЧАТАЕМОСТИ  — trimesh + manifold3d + pymeshlab: проверить
     watertight и согласованность нормалей; авторемонт; регенерация, если не чинится.
     Случайно слипшиеся тела — разделить обратно.
  5. ЦИКЛ САМОПРОВЕРКИ (≥95 %)  — отрендерить каждый объект с нескольких ракурсов,
     подать рендеры + исходный запрос (+ фото‑референсы) умной зрительной модели,
     оценить совпадение (геометрия, пропорции, полнота фич; для механики ещё —
     КОЛ‑ВО деталей, что объекты РАЗДЕЛЬНЫ, замеренные размеры vs спека).
     Если <95 %: диагностировать → поправить параметры CAD / регенерировать →
     перерендерить → переоценить. Цикл до порога или лимита итераций, затем
     показать тебе с уровнем уверенности и заметками.
  6. СЛАЙСИНГ (headless)  — Bambu Studio CLI: профиль машины A1 + профиль филамента
     PETG HF + профиль процесса с оверрайдами под гладкость+ironing (§6).
     Несколько STL + `--arrange 1` → раздельные объекты авто‑раскладкой → output.gcode.3mf.
  7. ВЫДАЧА  — залить .gcode.3mf на A1 по FTP / так, чтобы задание появилось в
     Bambu Handy; уведомить телефон «готово к проверке».
        │
        ▼
Ты: открываешь Bambu Handy → крутишь/смотришь нарезанную раскладку → жмёшь «Печать».
```

**Как план закрывает твои требования:**
- **Раздельные объекты, не монолит:** гарантируется на генерации (один STL на деталь) *и* перепроверяется в самопроверке (кол‑во деталей + отсутствие слипания + размеры каждой) *и* сохраняется при слайсинге (`--arrange 1`, режим «Split to Objects», никогда «Parts»).
- **≥95 % самопроверка:** зрительный цикл с явной рубрикой и лимитом итераций; агент сообщает финальную уверенность.
- **Уточнение до моделирования:** шаг 2 блокирует до твоего подтверждения.
- **Умная модель + сабагенты:** понимание запроса, написание CAD‑кода и оценка совпадения — на Fable 5/Opus 4.8; «как смоделировать X / какой стандарт у Y» — сабагенты‑ресёрчеры.
- **Настройка под PETG HF:** слайсинг всегда применяет профиль твоего филамента (§6), чтобы вывод был подогнан под пластик в машине.

---

## 4. Стек и ключевые инструменты

| Слой | Инструмент | Заметка |
|---|---|---|
| Мозг агента | Claude Agent SDK / Claude Code, модель Fable 5 → Opus 4.8 | сабагенты для ресёрча |
| Код‑CAD (точное) | **CadQuery / build123d** (ядро OCCT), **OpenSCAD + BOSL2** (шестерни) | watertight по построению |
| AI‑меш (органика) | **Meshy** REST API (экспорт STL/3MF) | нужен ремонт меша |
| Ремонт/проверка меша | **trimesh + manifold3d + pymeshlab**, `admesh` | ворота печатаемости |
| Слайсер (headless) | **Bambu Studio CLI** | оверрайды — через JSON‑профили, не флаги |
| Связь с принтером | локальный **MQTT (TLS 8883)** + **FTPS (990)**, либо `bambulabs-api` (Python) | нужен LAN + Developer Mode |
| Триггер Mac | **Raycast** script command + хоткей | поле ввода → сессия |
| Триггер iPhone | **Shortcuts** (кнопка действия) + `Run Script Over SSH` | текст/голос/фото |

---

## 5. Знания о принтере и печати (сжатая справка)

Полные версии — в папке `knowledge/`. Кратко:

**Bambu Lab A1 (полноразмерный):** зона печати 256×256×256 мм; текстурированная PEI‑пластина; **директ‑драйв** экструдер (поэтому ретракт короткий); сопло 0.4 мм, до 300 °C; до 500 мм/с; активная компенсация потока; авто‑калибровка; AMS Lite (4 цвета); **Wi‑Fi только 2.4 ГГц**. Открытая рама, без нагреваемой камеры → PLA/PETG/TPU отлично, ABS/ASA/PC не рекомендованы (коробление).

**Подключение для управления:** включи на экране принтера **LAN Mode + Developer Mode**; там же **Access Code** (пароль) и **серийный номер**. Локальный MQTT: `mqtts://<ip>:8883`, юзер `bblp`, пароль = access code, топики `device/<serial>/request|report`. Загрузка файла: **implicit FTPS, порт 990**, тот же логин. Печать без переслайсинга: нарезать один раз в `.gcode.3mf` → залить по FTP → MQTT `project_file` со стартом.

**Параметры и на что влияют (кратко):** меньше высота слоя → меньше видны слои на изгибах; слишком высокая температура сопла → нити/капли; мало верхних слоёв или низкий infill → «просадка»/дырки на верхе; слишком высокий flow → бугры/наплывы; ретракт лечит нити (у PETG критично); обдув выше → лучше нависания, но слабее спекание слоёв; скорость внешней стенки решает вид поверхности.

**Ironing (глажка верха):** после верхнего слоя сопло проходит ещё раз с **очень малым потоком**, разглаживая. Только по плоским верхним поверхностям. Параметры: тип (все верхние поверхности / только самый верх / все сплошные), паттерн (rectilinear), **flow % (у PETG ~10 %, поднимать осторожно — бугрит)**, шаг линий (~0.10 мм), скорость (~20–30 мм/с). Не помогает на стенках/изгибах и там, где важна точность верха; добавляет время.

---

## 6. Готовый профиль печати — Bambu PETG HF White Matte (гладкие модели)

Взять встроенный профиль филамента **«Bambu PETG HF»** + профиль процесса **A1 0.20 mm Quality**, затем применить:

**Филамент/температуры**
- Сопло **250–255 °C** (снизить до 240–245, если нити; держать ≥250, если слабое спекание)
- Стол **70 °C**, **текстурированная PEI** + тонкий слой клей‑карандаша (защита пластины)
- Камера — нет; при тёплой комнате приоткрыть/снять верх
- **Сушка перед печатью: 65 °C, 8 ч**
- Max volumetric speed: дефолт профиля **~21 мм³/с** (снизить до 16, если пузырит/шершавит)
- Обдув **40–50 %** (0 % первые 2–3 слоя)
- Один раз на катушку: калибровка **Flow Dynamics → Flow Ratio → (опц.) Max Volumetric → Ironing flow**

**Геометрия/качество**
- Высота слоя **0.16 мм** (0.12 для мелких деталей; 0.20 ради скорости); первый слой 0.20–0.24 мм
- Стенки **3**; внешняя стенка **~120 мм/с** ради вида
- Верхних слоёв **5** (≈0.8 мм), нижних **4**; верхний паттерн **Monotonic**
- Infill **15 %**, Grid/Gyroid; шов **Aligned** + wipe

**Ретракт/нити**
- Длина **0.8 мм** (до 1.2, если нити), скорость **~40 мм/с**, wipe + combing включены

**Ironing (ВКЛ, для гладкого верха)**
- Тип **все верхние поверхности**, паттерн rectilinear, **flow 10 %**, **шаг 0.10 мм**, **скорость ~20–30 мм/с**
- Прогнать быстрый тест глажки на купоне 40×40 мм, чтобы зафиксировать flow/скорость под эту матовую катушку

---

## 7. Настройка запуска

**Raycast (основной, Mac):** установить Raycast (бесплатно) → создать Script Command (bash/node), который принимает набранный текст как аргумент и запускает сессию агента в папке проекта с этим запросом → назначить глобальный хоткей. Печатаешь запрос прямо в поле Raycast, Enter — открывается интерактивная сессия (уточнения и результат видишь сразу). Фото — указать файлом/скриншотом.

**iPhone (на ходу):** Shortcut на **кнопке действия**: «Ask for Input»/«Dictate Text» (текст), «Record Audio» (голос), «Take Photo»/«Select Photos» (фото) → действие **«Run Script Over SSH»** заходит на Mac и стартует сессию агента, передав текст/файлы. Уточнения приходят push‑уведомлением; результат появляется в Bambu Handy. Тот же Shortcut можно добавить в Пункт управления и на экран «Домой».

**Без демона:** ничего постоянно не висит. В начале каждой сессии агент пингует A1 по MQTT и предупреждает, если принтер выключен.

---

## 8. Этапы сборки (что Fable 5 сделает по порядку)

1. **Скелет проекта на Mac** (Claude Code / Agent SDK; сессия по требованию, без демона).
2. **Триггеры:** Raycast script command (хоткей → поле → запуск с запросом) + iPhone Shortcut на кнопке действия (текст/голос/фото → SSH → старт сессии).
3. **Модуль понимания + уточнения** (структурная спека, блокировка до подтверждения).
4. **Гибридная генерация** (CadQuery/OpenSCAD‑BOSL2 + Meshy), один STL на объект.
5. **Ворота печатаемости** (trimesh/manifold3d/pymeshlab; разделение слипшихся тел).
6. **Цикл самопроверки со зрением** (рубрика ≥95 %, лимит итераций, отчёт уверенности).
7. **Слайсинг Bambu Studio CLI** с профилем PETG HF (§6), `--arrange 1` для раздельных объектов.
8. **Выдача:** FTP/MQTT → задание видно в Bambu Handy → уведомление на телефон.
9. **Сквозной тест** на известной паре: прямозубая шестерня Ø20 мм (проверка точности/раздельности) + простая фигурка (проверка органики).

---

## 9. ⭐ Мастер‑промпт для Fable 5 (вставить целиком)

> Открой Fable 5 (или Opus 4.8) в папке проекта на Mac и вставь всё, что ниже.

```
You are building a local "3D Print Agent" that runs on my Mac and drives my Bambu Lab A1.
Follow the plan in PLAN-3D-AGENT.md in this repo. Build it in the staged order in §8.

ENVIRONMENT (fixed):
- Backend runs on my Mac, on the same Wi‑Fi as the A1. Launch is ON‑DEMAND (no daemon):
  each trigger starts a fresh agent session.
- The A1 is (or will be) in LAN Mode + Developer Mode. Local control only:
  MQTT mqtts://<ip>:8883 (user bblp, pass = LAN access code, topics device/<serial>/request|report),
  and implicit‑FTPS upload on port 990. Prefer the `bambulabs-api` Python lib; fall back to raw MQTT/FTP.
- Filament in the machine: Bambu PETG HF White Matte. Always slice with the PETG HF profile in §6.
- Final handoff: upload the sliced .gcode.3mf so the job appears in Bambu Handy; I press Print there.

TRIGGERS:
- Primary (Mac): a Raycast script command bound to a hotkey. It takes typed text as an argument and
  opens an interactive agent session in the project with that request.
- Secondary (iPhone): an Apple Shortcut on the Action Button that collects text (Ask for Input/Dictate),
  audio (Record Audio), and photos (Take Photo/Select Photos), then uses "Run Script Over SSH" to start
  the same session on the Mac with the text/files attached. Deliver clarifications via push; the result
  appears in Bambu Handy.
- At session start, ping the A1 over MQTT and warn me if the printer is off/unreachable.

BRAIN:
- Use the smartest available model (Fable 5, else Opus 4.8) for intent parsing, CAD code authoring,
  and the self‑check scoring. Spin up research subagents for "how to model X / what standard for Y".

PIPELINE (implement exactly):
1) UNDERSTAND: parse my text + transcribe audio + read photos into a STRUCTURED build‑spec:
   object list, per‑object dimensions, mechanical‑vs‑organic, part count, tolerances, constraints.
2) CLARIFY: restate your understanding and ask targeted questions. BLOCK until I confirm/correct.
   Do not model before confirmation.
3) GENERATE (hybrid router):
   - precise/mechanical (gears, brackets, threaded, dimensioned) → write CadQuery/build123d (OCCT)
     or OpenSCAD + BOSL2 for gears. Emit ONE STL PER DISTINCT OBJECT, each individually dimensioned.
   - organic/figurine → Meshy text/image‑to‑3D API → mesh.
4) PRINTABILITY GATE: with trimesh + manifold3d + pymeshlab, assert watertight AND winding‑consistent;
   auto‑repair; regenerate if unfixable. If a scene came back as one merged body, split it into separate
   bodies so each object stays independent.
5) SELF‑CHECK LOOP (>=95%): offscreen‑render each object from multiple angles; feed renders + my original
   request (+ reference photos) to the vision model; score match on geometry, proportions, feature
   completeness, and — for mechanical — PART COUNT, that objects are SEPARATE (not merged), and MEASURED
   dimensions vs the spec. If <95%, diagnose, edit CAD params / regenerate, re‑render, re‑score. Loop to
   threshold or a max‑iteration cap, then present with your confidence and notes. Never hand me a part
   you scored below 95% without flagging it.
6) SLICE (headless): Bambu Studio CLI with the A1 machine profile + PETG HF filament profile + a process
   profile carrying the smooth+ironing overrides from §6. Pass all STLs together with --arrange 1 so they
   are laid out as SEPARATE objects on one plate. Output a .gcode.3mf (zip containing Metadata/plate_1.gcode).
   Do per‑parameter control by editing the process/filament JSON, not undocumented CLI flags.
7) HANDOFF: FTP the .gcode.3mf to the A1 so it's startable from Bambu Handy; notify my phone
   "ready to review in Handy."

HARD REQUIREMENTS (acceptance criteria — test these):
- Multi‑object requests yield N SEPARATE objects on the plate with correct per‑object sizes (e.g. "6 gears"
  → 6 distinct STLs, 6 objects after slicing), never one fused model.
- The >=95% self‑check loop actually runs and is reported.
- The clarify step blocks until I confirm.
- Slicing always applies the PETG HF profile in §6 (incl. ironing on).
- The whole thing launches on‑demand from the Raycast hotkey and from the iPhone Action Button.
- The sliced job shows up in Bambu Handy for my final review + Print.

FRAGILITY TO HANDLE:
- Bambu firmware auth: rely on LAN Developer Mode; handle the printer's self‑signed TLS cert (don't verify
  or pin it). Pin a validated Bambu Studio version.
- Bambu Studio CLI can fail to load external presets — export validated machine/process/filament JSONs from
  a working GUI config and load those.
- AI meshes are often non‑manifold — always run the printability gate; prefer code‑CAD for anything precise.
- iOS media quirks — use the Shortcut for intake and Bambu Handy for review (avoid fragile web‑media paths).

FINAL STEP: run the end‑to‑end test in §8 (a 20mm spur gear + a simple figurine) and show me the results.
```

---

## 10. Риски (озвучены, не блокирующие)

- **Прошивка Bambu:** сторонний контроль держится на открытом LAN Developer Mode; закрепи прошивку, тестируй перед обновлением.
- **AI‑меши** органики иногда требуют ремонта/регенерации — ворота печатаемости и самопроверка это гасят, но органика менее детерминирована, чем код‑CAD.
- **Загрузка внешних пресетов в Bambu Studio CLI** капризна — экспортируй проверенные JSON из рабочего GUI‑конфига и закрепи версию Studio.
- **Медиа на iOS в вебе** глючноваты — поэтому ввод через Shortcut, а проверка в Bambu Handy.

---

## 11. Где остальные материалы

- `knowledge/` — 5 подробных заметок: принтер, параметры (симптом→причина→фикс), ironing, сравнение пластиков, профиль PETG HF.
- `blueprint/` — архитектура агента, мастер‑промпт для Fable 5, точные JSON‑оверрайды слайсера, шпаргалка по управлению принтером, настройка триггеров.
