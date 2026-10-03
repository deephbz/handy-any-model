#!/usr/bin/env bash
# Install PoC dependencies outside the source tree.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${HOME}/.cache/handy-cloud/venv"
uv venv --python 3.12 --allow-existing "$VENV"
uv pip sync --python "$VENV/bin/python" "$ROOT/server/requirements.txt"
"$VENV/bin/python" - <<'PY'
from mlx_audio.stt.utils import load_model
for name in ['mlx-community/parakeet-tdt-0.6b-v3', 'mlx-community/Qwen3-ASR-1.7B-4bit', 'mlx-community/Qwen3-ASR-1.7B-8bit', 'mlx-community/granite-speech-4.1-2b-nar-mlx-5bit']:
    model = load_model(name)
    del model
from fermion._speech import fetch
from fermion.transcribe import _resolve
repo, key, pin, local_dir = _resolve('phonon-2')
fetch.ensure(repo, key, pin)
PY
python3 - "$ROOT" "$VENV" <<'PY'
import pathlib, plistlib, sys
root, venv = map(pathlib.Path, sys.argv[1:])
cache = pathlib.Path.home() / '.cache/handy-cloud'
config = {'Label': 'local.handy-cloud.asr', 'ProgramArguments': [str(venv / 'bin/python'), str(root / 'server/launch.py')], 'WorkingDirectory': str(root), 'RunAtLoad': True, 'KeepAlive': True, 'StandardOutPath': str(cache / 'launchd.log'), 'StandardErrorPath': str(cache / 'launchd.log'), 'EnvironmentVariables': {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HF_HUB_OFFLINE': '1'}}
(root / 'server/local.handy-cloud.asr.plist').write_bytes(plistlib.dumps(config))
config['Label'] = 'local.handy-cloud.phonon'
config['ProgramArguments'] = [str(venv / 'bin/fermion'), 'serve', 'phonon-2', '--host', '127.0.0.1', '--port', '8179']
config['StandardOutPath'] = str(cache / 'phonon-launchd.log')
config['StandardErrorPath'] = str(cache / 'phonon-launchd.log')
(root / 'server/local.handy-cloud.phonon.plist').write_bytes(plistlib.dumps(config))
PY
