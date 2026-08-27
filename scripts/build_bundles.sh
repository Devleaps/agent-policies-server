#!/usr/bin/env bash
# Build one self-contained OPA bundle .tar.gz per policy bundle.
#
# `helpers` is a shared Rego dependency (imported by universal, python_uv,
# python_pip, demo_bundles, demo_flags) and OPA bundle roots cannot overlap,
# so a bundle built without it fails to compile standalone. Every output
# bundle therefore merges in policies/helpers at build time, making each
# .tar.gz self-contained: the client only ever configures the bundle it
# actually wants (e.g. "universal"), never "helpers" separately.
set -euo pipefail

POLICIES_DIR="policies"
OUTPUT_DIR="bundles"
REVISION="${1:-$(git rev-parse HEAD)}"

# Bundles that are distributed standalone. helpers is a dependency-only
# bundle and is never shipped on its own.
BUNDLES=(universal python_uv python_pip demo_bundles demo_flags)

mkdir -p "$OUTPUT_DIR"

for bundle in "${BUNDLES[@]}"; do
  echo "Building ${bundle}.tar.gz (revision ${REVISION})..."
  opa build \
    -b "${POLICIES_DIR}/${bundle}" \
    -b "${POLICIES_DIR}/helpers" \
    -r "$REVISION" \
    -o "${OUTPUT_DIR}/${bundle}.tar.gz"
done

echo "Verifying all bundles compile independently..."
for bundle in "${BUNDLES[@]}"; do
  opa check "${POLICIES_DIR}/${bundle}" "${POLICIES_DIR}/helpers" >/dev/null
done

echo "Built ${#BUNDLES[@]} bundles into ${OUTPUT_DIR}/:"
ls -lh "$OUTPUT_DIR"
