# Blueprint — Шпаргалка по управлению Bambu A1 (локально)

> Всё сторонее управление — **неофициальное/реверс‑инженерное**. Держи A1 в **LAN Mode + Developer Mode**.

## Включить доступ
1. Экран принтера → Settings (шестерёнка) → сеть/LAN.
2. Включить **LAN Mode** и **Developer Mode**.
3. Записать **Access Code** (пароль) и **серийный номер** (там же / в Studio / в Handy).
4. Узнать **IP** принтера (экран сети / роутер).

## MQTT (управление + статус)
- Эндпоинт: `mqtts://<printer-ip>:8883`, **TLS обязателен**. Юзер `bblp`, пароль = **Access Code**.
- Сертификат самоподписанный → либо вытянуть (`openssl s_client -showcerts -connect <ip>:8883`), либо **отключить проверку сертификата** в клиенте (стандартная практика библиотек).
- Топики: подписка `device/<serial>/report`; публикация `device/<serial>/request`. У каждой команды `sequence_id` для сопоставления ответа.

### Полезные команды (JSON payload в `.../request`)
Старт нарезанного 3MF, уже лежащего на устройстве:
```json
{"print":{"command":"project_file","param":"Metadata/plate_1.gcode",
  "url":"file:///mnt/sdcard","subtask_name":"job",
  "bed_type":"auto","bed_levelling":true,"flow_cali":true,"use_ams":false}}
```
(`url` также может быть `ftp:///<файл>.3mf` или `ftp:///cache/...` для файла, залитого по FTP.)

Старт сырого gcode: `{"print":{"command":"gcode_file","param":"filename.gcode"}}`
Пауза/Продолжить/Стоп: `{"print":{"command":"pause"|"resume"|"stop","param":""}}` (QoS 1)
Полный статус: `{"pushing":{"command":"pushall","version":1,"push_target":1}}`
Ещё: `gcode_line` (инлайн gcode), `ledctrl` (свет) и т. д.

## FTP (загрузка нарезанного файла)
- **Implicit FTPS, порт 990**, юзер `bblp`, пароль = Access Code. Файлы ложатся на SD/`cache`.
- Так `.gcode.3mf` попадает на A1 перед MQTT‑стартом `project_file`.
- Implicit‑FTPS + самоподписанный сертификат ломают многие стоковые FTP‑клиенты — бери библиотеку, которая это умеет.

## Печать без переслайсинга (целевой поток)
1. Нарезать один раз → получить **`.gcode.3mf`** (zip с `Metadata/plate_1.gcode`).
2. **Залить по FTP** на принтер.
3. **MQTT `project_file`** с `param:"Metadata/plate_1.gcode"` (и нужным `plate_number`) → печать без повторного слайсинга.

## Библиотеки (Python, неофициальные)
| Либа | Что умеет |
|---|---|
| **`bambulabs-api`** | MQTT‑контроль + FTP‑загрузка + старт печати; `Printer(ip, access_code, serial)`, `upload_file(...)`, `start_print(name, plate)` — **лучший выбор** |
| `pybambu` (в `ha-bambulab`) | самая обкатанная модель статуса (референс схемы `report`) |
| `bambu-connect` | статус, отправка заданий, gcode, камера |
| `bambu-lab-cloud-api` | облако + MQTT + локальный FTP, 2FA‑логин |
| `OpenBambuAPI` (доки) | каноничный реверс‑спек протокола |
| `bambu-mcp` | MCP‑обёртка (MQTT/FTP/камера/AMS), если агент говорит по MCP |

## Облако (если однажды понадобится, не для LAN)
- Хост `https://api.bambulab.com`. Логин `POST /v1/user-service/user/login` → **обязательный 2FA email‑код** → `accessToken` (JWT ~24 ч). Список устройств `GET /v1/iot-service/api/user/bind`. Рейт‑лимит ~5/мин.
- Для агента в одной сети **используй локальный MQTT+FTP**, не облако (2FA, ротация токенов, лимиты, риск TOS).

## Хрупкость
- **Authorization Control System** (прошивка янв‑2025): старт печати/движение/температуры/AMS/видео за авторизацией. Спасает **LAN Developer Mode** (MQTT/стрим/FTP открыты без авторизации). Может измениться будущей прошивкой — закрепи прошивку, тестируй перед апдейтом.

## Источники
- OpenBambuAPI/mqtt.md (Doridian); forum «MQTT for A1»; forum «FTP on P1/A1»; bambulabs‑api docs; Bambu blog + Hackaday + 3DPI про Authorization Control System.
