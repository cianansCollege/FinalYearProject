#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/submission"
DEFAULT_NAME="FYP_submission_$(date +%Y%m%d_%H%M%S)"
BUNDLE_NAME="${1:-$DEFAULT_NAME}"
BUNDLE_NAME="${BUNDLE_NAME%.zip}"
STAGING_DIR="$OUTPUT_DIR/$BUNDLE_NAME"
ZIP_PATH="$OUTPUT_DIR/$BUNDLE_NAME.zip"
SOURCES=(
  "README.md"
  "Prototype4"
  "FinalReport"
)

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' is not installed." >&2
    exit 1
  fi
}

require_command rsync
require_command zip

mkdir -p "$OUTPUT_DIR"
rm -rf "$STAGING_DIR" "$ZIP_PATH"
mkdir -p "$STAGING_DIR"

for source in "${SOURCES[@]}"; do
  if [ ! -e "$ROOT_DIR/$source" ]; then
    echo "Warning: skipping missing path '$source'" >&2
    continue
  fi

  rsync \
    --archive \
    --prune-empty-dirs \
    --exclude '.git/' \
    --exclude 'submission/' \
    --exclude '.venv/' \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '.ipynb_checkpoints/' \
    --exclude '.DS_Store' \
    --exclude '*.wav' \
    --exclude '*.mp3' \
    --exclude '*.m4a' \
    --exclude '*.flac' \
    --exclude '*.ogg' \
    --exclude '*.aria2' \
    --exclude '*.tar.gz' \
    --exclude '*.pt' \
    --exclude '*.h5' \
    --exclude '*.sqlite3' \
    "$ROOT_DIR/$source" "$STAGING_DIR/"
done

(
  cd "$OUTPUT_DIR"
  zip -qr "$(basename "$ZIP_PATH")" "$(basename "$STAGING_DIR")"
)

rm -rf "$STAGING_DIR"

echo "Created submission bundle:"
echo "$ZIP_PATH"
du -sh "$ZIP_PATH"
