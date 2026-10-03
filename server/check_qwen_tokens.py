"""Check token-budget saturation on the longest benchmark inputs in both Qwen variants."""
import json
from pathlib import Path
from mlx_audio.stt.utils import load_model
import mlx.core as mx

root = Path(__file__).resolve().parent.parent
rows = []
for filename in ['manifest.json', 'accuracy-manifest.json', 'meeting-manifest.json']:
    rows.extend(json.loads((root / 'samples' / filename).read_text()))
long_audio = max(rows, key=lambda r:r['duration_s'])
long_reference = max(rows, key=lambda r:len(r['reference'].split()))
selected = {r['file']: r for r in [long_audio, long_reference]}
checks = []
for name in ['mlx-community/Qwen3-ASR-1.7B-4bit', 'mlx-community/Qwen3-ASR-1.7B-8bit']:
    model = load_model(name)
    for row in selected.values():
        result = model.generate(str(root / 'samples' / row['file']), max_tokens=1024, language='en', chunk_duration=30, prefill_step_size=2048)
        checks.append({'model': name, 'file': row['file'], 'duration_s': row['duration_s'], 'reference_words': len(row['reference'].split()), 'generation_tokens': result.generation_tokens, 'max_tokens': 1024, 'budget_saturated': result.generation_tokens >= 1024, 'text': result.text})
    del model
    mx.clear_cache()
(root / 'server/qwen-token-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
