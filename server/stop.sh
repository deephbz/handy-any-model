#!/usr/bin/env bash
# Stop only recorded PoC processes. Keep Phonon during isolated MLX benchmarks.
set -euo pipefail
stop_recorded() {
  local PIDFILE="$1" MATCH="$2"
  [[ -f "$PIDFILE" ]] || return 0
  local PID COMMAND
  PID="$(< "$PIDFILE")"
  [[ "$PID" =~ ^[0-9]+$ ]] || return 1
  COMMAND="$(ps -p "$PID" -o command= || true)"
  if [[ -z "$COMMAND" ]]; then rm -f "$PIDFILE"; return 0; fi
  if [[ "$COMMAND" != *"$MATCH"* ]]; then
    echo "Recorded PID does not match $MATCH; no process was stopped." >&2
    return 1
  fi
  kill "$PID"
  for i in {1..30}; do
    if ! kill -0 "$PID" 2>/dev/null; then rm -f "$PIDFILE"; return 0; fi
    sleep 1
  done
  echo 'Process has not stopped; inspect it before restarting.' >&2
  return 1
}
stop_recorded "$HOME/.cache/handy-cloud/server.pid" 'server/launch.py'
if [[ "${1:-}" != --mlx-only ]]; then
  stop_recorded "$HOME/.cache/handy-cloud/phonon.pid" 'fermion serve'
fi
