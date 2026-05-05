#!/bin/bash
# Check if OrcaSlicer is installed on macOS

PATHS=(
  "/Applications/OrcaSlicer.app"
  "$HOME/Applications/OrcaSlicer.app"
)

for p in "${PATHS[@]}"; do
  if [ -d "$p" ]; then
    echo "✅ OrcaSlicer found at: $p"
    exit 0
  fi
done

echo "❌ OrcaSlicer not found."
echo "   Download from: https://github.com/SoftFever/OrcaSlicer/releases/latest"
echo "   Install the .dmg for macOS."
exit 1
