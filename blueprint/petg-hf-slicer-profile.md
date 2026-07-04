# Blueprint — Профиль слайсера для PETG HF (оверрайды + команды CLI)

Точный контроль в Bambu Studio/Orca CLI делается **редактированием JSON‑профилей процесса/филамента**,
а не недокументированными флагами. Ниже — что переопределить и как вызвать CLI.

## Оверрайды процесса (ключ → значение)
> Имена ключей могут чуть отличаться по версии Studio — сверься с экспортированным из GUI JSON.

| Смысл | Ключ (ориентир) | Значение |
|---|---|---|
| Высота слоя | `layer_height` | `0.16` |
| Первый слой | `initial_layer_print_height` | `0.2` |
| Стенки | `wall_loops` | `3` |
| Верхних слоёв | `top_shell_layers` | `5` |
| Нижних слоёв | `bottom_shell_layers` | `4` |
| Верхний паттерн | `top_surface_pattern` | `monotonic` |
| Заполнение | `sparse_infill_density` | `15%` |
| Паттерн infill | `sparse_infill_pattern` | `grid` (или `gyroid`) |
| Скорость внешней стенки | `outer_wall_speed` | `120` |
| Шов | `seam_position` | `aligned` |
| **Ironing тип** | `ironing_type` | `top` (all top surfaces) |
| Ironing паттерн | `ironing_pattern` | `rectilinear` |
| **Ironing flow** | `ironing_flow` | `10%` |
| **Ironing шаг** | `ironing_spacing` | `0.1` |
| **Ironing скорость** | `ironing_speed` | `25` |

## Оверрайды филамента (PETG HF)
| Смысл | Ключ (ориентир) | Значение |
|---|---|---|
| Температура сопла | `nozzle_temperature` | `252` |
| Первый слой сопла | `nozzle_temperature_initial_layer` | `255` |
| Температура стола (текстурная PEI) | `hot_plate_temp` / `textured_plate_temp` | `70` |
| Обдув мин/макс | `fan_min_speed` / `fan_max_speed` | `40` / `50` |
| Обдув первых слоёв | `close_fan_the_first_x_layers` | `2` |
| Max volumetric speed | `filament_max_volumetric_speed` | `21` (→ `16` если пузырит) |
| Ретракт длина | `retraction_length` | `0.8` |
| Ретракт скорость | `retraction_speed` | `40` |
| Wipe | `wipe` | `1` |

## Вызов CLI (Bambu Studio)
Один объект:
```
bambu-studio \
  --slice 1 \
  --load-settings "A1_machine.json;PETG_HF_process.json" \
  --load-filaments "PETG_HF_filament.json" \
  --skip-useless-pick \
  --export-3mf out.gcode.3mf \
  model.stl
```

Несколько объектов (раздельно на одной плите):
```
bambu-studio \
  --slice 1 \
  --arrange 1 \
  --load-settings "A1_machine.json;PETG_HF_process.json" \
  --load-filaments "PETG_HF_filament.json" \
  --skip-useless-pick \
  --export-3mf out.gcode.3mf \
  gear1.stl gear2.stl gear3.stl gear4.stl gear5.stl gear6.stl
```

- `--export-3mf` даёт **архив с gcode** (`Metadata/plate_1.gcode` внутри), а не сырой .gcode.
- `--arrange 1` раскладывает переданные STL как **отдельные объекты**.
- Для детерминированных позиций/плит есть недокументированный `--load-assemble-list assemble_list.json`
  (плиты, объекты, путь/кол‑во/филамент/pos_x/pos_y). Использовать при нужде в точных координатах.

## Важные оговорки
- «Split to **Objects**» — объекты остаются раздельно‑раскладываемыми; «Split to **Parts**» — сливает в один объект, Arrange их не разнесёт. Держи каждую сгенерированную деталь **отдельным объектом/файлом**.
- CLI может ругаться на внешние пресеты («cannot load settings from JSON») — экспортируй точные machine/process/filament JSON из рабочего GUI‑конфига и грузи их; закрепи версию Studio.
- Профили PETG‑HF исторически имели баги видимости/детекции — валидируй на своей версии.

## Источники
- BambuStudio wiki: Command‑Line Usage; Printago CLI reference; OrcaSlicer discussion #8593; Bambu wiki Split to Objects/Parts; forum по расположению профилей.
