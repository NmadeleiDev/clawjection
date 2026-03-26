#!/usr/bin/env bash
set -eu

ACTION="${1:-apply}"
OPENCLAW_CONFIG_PATH="${HOME}/.openclaw/openclaw.json"

if [ $# -gt 0 ]; then
  shift
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --openclaw-config-path)
      OPENCLAW_CONFIG_PATH="${2:?missing config path}"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

RESULT_PATH="${CLAWJECTION_RESULT_PATH:-./clawjection-result.json}"

cat > "$RESULT_PATH" <<EOF
{
  "status": "ok",
  "summary": "Minimal example completed for action '${ACTION}'.",
  "artifacts": [
    "${OPENCLAW_CONFIG_PATH}"
  ]
}
EOF
