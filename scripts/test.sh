#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "==> opa check"
opa check policies

echo "==> regal lint"
regal lint policies

echo "==> opa test"
opa test policies -v

echo "==> pytest"
uv run pytest
