#!/usr/bin/env bash
# Start one loopback-only server; refuse an occupied port.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$HOME/.cache/handy-cloud"
mkdir -p "$CACHE"
if lsof -nP -iTCP:8178 -sTCP:LISTEN >/dev/null 2>&1; then
  echo 'Port 8178 is occupied; keep the current server or stop it first.' >&2
  exit 1
fi
if ! lsof -nP -iTCP:8179 -sTCP:LISTEN >/dev/null 2>&1; then
  HF_HUB_OFFLINE=1 nohup "$CACHE/venv/bin/fermion" serve phonon-2 --host 127.0.0.1 --port 8179 >> "$CACHE/phonon.log" 2>&1 &
  echo $! > "$CACHE/phonon.pid"
fi
for i in {1..60}; do
  if curl -fsS http://127.0.0.1:8179/health >/dev/null 2>&1; then break; fi
  sleep 1
done
"$CACHE/venv/bin/python" - <<'PY'
import json, urllib.request
with urllib.request.urlopen('http://127.0.0.1:8179/v1/models', timeout=5) as response:
    names = {x['id'] for x in json.load(response)['data']}
assert 'FermionResearch/Phonon-2' in names, 'Unexpected service on port 8179'
PY
HF_HUB_OFFLINE=1 nohup "$CACHE/venv/bin/python" "$ROOT/server/launch.py" >> "$CACHE/server.log" 2>&1 &
echo $! > "$CACHE/server.pid"
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8178/openapi.json >/dev/null 2>&1; then
    echo "ASR server PID $(< "$CACHE/server.pid") on 127.0.0.1:8178"
    exit 0
  fi
  sleep 1
done
echo "Server did not become ready. Read $CACHE/server.log" >&2
exit 1
