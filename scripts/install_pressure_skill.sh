#!/usr/bin/env bash
# Copy canonical .cursor/skills/pressure-skill to user agent skill dirs.
# Usage (from repo root):
#   bash scripts/install_pressure_skill.sh
#   bash scripts/install_pressure_skill.sh all
#   bash scripts/install_pressure_skill.sh cursor agents

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/.cursor/skills/pressure-skill"
NAME="pressure-skill"

if [[ ! -d "$SRC" ]]; then
  echo "Source skill folder not found: $SRC" >&2
  exit 1
fi

install_one() {
  local label="$1"
  local dst_root="$2"
  local dst="$dst_root/$NAME"
  mkdir -p "$dst_root"
  rm -rf "$dst"
  cp -R "$SRC" "$dst"
  echo "[$label] -> $dst"
}

if [[ $# -eq 0 ]] || [[ "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" == "all" ]]; then
  CHOSEN=(cursor agents claude openclaw)
else
  CHOSEN=("$@")
fi

for t in "${CHOSEN[@]}"; do
  t_lc=$(printf '%s' "$t" | tr '[:upper:]' '[:lower:]')
  case "$t_lc" in
    cursor)   install_one "Cursor"     "$HOME/.cursor/skills" ;;
    agents)   install_one "Agents"     "$HOME/.agents/skills" ;;
    claude)   install_one "ClaudeCode" "$HOME/.claude/skills" ;;
    openclaw) install_one "OpenClaw"   "$HOME/.openclaw/workspace/skills" ;;
    *)
      echo "Unknown target: $t (use cursor|agents|claude|openclaw|all)" >&2
      exit 1
      ;;
  esac
done

echo ""
echo "Skill files installed. Run bundle_local.py / uvicorn from this repo root (contains scripts/)."
