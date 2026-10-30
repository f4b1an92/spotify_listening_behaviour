#!/usr/bin/env bash
# Builds lambda_layer_from_python3.13/python.zip for AWS Lambda (Python 3.13, x86_64). Run inside the 'spotify' conda env.
set -euo pipefail

cd "$(dirname "$0")"

OUT_DIR=lambda_layer_from_python3.13
REQUIREMENTS=requirements-layer313.txt

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/python"

# Download Linux wheels instead of macOS ones; Lambda (AL2023) has glibc 2.34.
python -m pip install -r "$REQUIREMENTS" \
  --target "$OUT_DIR/python" \
  --platform manylinux_2_28_x86_64 \
  --python-version 3.13 \
  --implementation cp \
  --only-binary=:all: \
  --upgrade

rm -rf "$OUT_DIR/python/bin"
find "$OUT_DIR/python" -type d -name "__pycache__" -prune -exec rm -rf {} +

# Fail if any non-Linux binary slipped in.
if find "$OUT_DIR/python" -name "*darwin*" | grep -q .; then
  echo "ERROR: macOS binaries found in layer" >&2
  exit 1
fi

(cd "$OUT_DIR" && zip -qr python.zip python)

echo "Unzipped size (limit 250 MB incl. function code):"
du -sh "$OUT_DIR/python"
echo "Zipped size (console upload limit 50 MB, otherwise use S3):"
du -h "$OUT_DIR/python.zip"
python -m pip freeze --path "$OUT_DIR/python"
