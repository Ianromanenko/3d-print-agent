#!/bin/bash
# Dev startup script
set -e
cd "$(dirname "$0")/.."

echo "🖨️  3D Print Agent — Dev Mode"
echo ""
echo "Checking dependencies…"
[ -d node_modules ] || npm install

echo "Starting server…"
npm run dev
