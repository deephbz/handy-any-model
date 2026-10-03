#!/usr/bin/env bash
# Run the accepted candidates on identical smoke and held-out accuracy manifests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$HOME/.cache/handy-cloud/venv/bin/python"
mkdir -p server/benchmarks
while read -r KEY MODEL; do
  ./server/stop.sh --mlx-only
  ./server/start.sh
  EXTRA=()
  if [[ "$KEY" == phonon ]]; then
    EXTRA=(--extra-pid "$(< "$HOME/.cache/handy-cloud/phonon.pid")")
  fi
  "$PY" samples/benchmark.py --model "$MODEL" "${EXTRA[@]}" --output "server/benchmarks/$KEY-smoke.json"
  "$PY" samples/benchmark.py --model "$MODEL" "${EXTRA[@]}" --manifest "$ROOT/samples/accuracy-manifest.json" --repeats 1 --output "server/benchmarks/$KEY-accuracy.json"
  "$PY" samples/benchmark.py --model "$MODEL" "${EXTRA[@]}" --manifest "$ROOT/samples/meeting-manifest.json" --repeats 1 --output "server/benchmarks/$KEY-meeting.json"
done <<'MODELS'
parakeet mlx-community/parakeet-tdt-0.6b-v3
qwen4 mlx-community/Qwen3-ASR-1.7B-4bit
qwen8 mlx-community/Qwen3-ASR-1.7B-8bit
phonon FermionResearch/Phonon-2
granite mlx-community/granite-speech-4.1-2b-nar-mlx-5bit
MODELS
