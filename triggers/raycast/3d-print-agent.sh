#!/bin/bash
#
# Raycast Script Command — основной триггер на Mac (§7 плана, blueprint/launch-setup.md §A).
# Установка:
#   1. Установить Raycast (бесплатно).
#   2. Raycast → Extensions → Script Commands → Add → указать папку со скриптами,
#      или скопировать этот файл в свою Raycast Script Commands папку.
#   3. Назначить глобальный хоткей на команду «3D Print Agent».
#   4. Хоткей → печатаешь запрос → Enter. Фото — путём к файлу в тексте запроса.
#
# @raycast.schemaVersion 1
# @raycast.title 3D Print Agent
# @raycast.mode fullOutput
# @raycast.packageName 3D Print
# @raycast.icon 🖨️
# @raycast.argument1 { "type": "text", "placeholder": "Что напечатать?" }
#
# @raycast.description Генерирует модель из текста → gate → слайсинг PETG HF → в Bambu Handy.
# @raycast.author Yan
set -euo pipefail

REQUEST="$1"

# Путь к репозиторию агента. Поправь, если проект лежит в другом месте.
REPO_DIR="$HOME/Claude/work/3d-print-agent"

exec "$REPO_DIR/bin/print-agent" "$REQUEST"
