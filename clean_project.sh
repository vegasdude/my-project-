#!/usr/bin/env bash
#
# clean_project.sh - Remove common build and cache artifacts.
# Usage: ./clean_project.sh [path]
#
# If no path is given, it runs in the current directory.

set -euo pipefail

TARGET_DIR="${1:-.}"

echo "[clean_project] Cleaning in: ${TARGET_DIR}"

# Patterns to remove; extend as needed.
PATTERNS=(
  "__pycache__"
  "*.pyc"
  "*.pyo"
  "*.log"
  "node_modules"
  "dist"
  "build"
  ".pytest_cache"
  ".mypy_cache"
  ".DS_Store"
)

for pattern in "${PATTERNS[@]}"; do
  echo "  - Removing '${pattern}'"
  find "${TARGET_DIR}" -name "${pattern}" -print0 2>/dev/null | xargs -0 rm -rf || true
done

echo "[clean_project] Done."