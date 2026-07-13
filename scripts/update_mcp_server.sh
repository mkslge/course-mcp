#!/usr/bin/env bash
set -euo pipefail

SERVER_NAME="${SERVER_NAME:-course-mcp}"
ROOT_DIR="${ROOT_DIR:-/Users/markseeliger/Desktop/Classes/UMD}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI is not installed or is not on PATH" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed or is not on PATH" >&2
  exit 1
fi

if [[ ! -d "$ROOT_DIR" ]]; then
  echo "ROOT_DIR does not exist: $ROOT_DIR" >&2
  echo "Set ROOT_DIR before running this script." >&2
  exit 1
fi

if codex mcp get "$SERVER_NAME" >/dev/null 2>&1; then
  codex mcp remove "$SERVER_NAME"
fi

codex mcp add "$SERVER_NAME" \
  --env "ROOT_DIR=$ROOT_DIR" \
  -- uv --directory "$PROJECT_DIR" run course-mcp

codex mcp get "$SERVER_NAME"
