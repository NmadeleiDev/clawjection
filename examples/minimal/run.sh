#!/usr/bin/env bash
set -eu

RESULT_PATH="${CLAWJECTION_RESULT_PATH:-./clawjection-result.json}"

cat > "$RESULT_PATH" <<'EOF'
{
  "status": "ok",
  "summary": "Minimal example completed."
}
EOF
