#!/usr/bin/env bash
# Usage: ./scripts/run_and_log.sh /path/to/logfile -- command args...
set -uo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 LOGFILE -- command [args...]" >&2
  exit 2
fi
LOGFILE=$1
shift
if [ "$1" != "--" ]; then
  echo "Missing -- separator" >&2
  exit 2
fi
shift
CMD=("$@")
mkdir -p "$(dirname "$LOGFILE")"
(
  echo "=== RUN: $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="
  echo "Command: ${CMD[*]}"
  echo
  "${CMD[@]}"
) >"$LOGFILE" 2>&1
EXIT=$?
echo "=== EXIT: $EXIT ===" >>"$LOGFILE"
echo "$EXIT" >"${LOGFILE}.exit"
exit $EXIT
