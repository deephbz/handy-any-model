"""Measure a fresh-process cached model load. Run once per candidate."""
import argparse
import json
from pathlib import Path
import resource
import time
import mlx.core as mx

parser = argparse.ArgumentParser()
parser.add_argument('model')
parser.add_argument('output', type=Path)
args = parser.parse_args()
if args.model == 'FermionResearch/Phonon-2':
    from fermion._speech import backends, fetch
    from fermion.transcribe import _resolve
    catalog, key, pin, local_dir = _resolve('phonon-2')
    # The model is already cached. Resolution and download are outside the timer.
    model_dir = local_dir if local_dir is not None else fetch.ensure(catalog, key, pin)
    start = time.perf_counter()
    model = backends.load('mlx', model_dir, profile=key, backend=pin['backend'], quiet=True)
    load_s = time.perf_counter() - start
    disk_bytes = sum(p.stat().st_size for p in Path(model_dir).rglob('*') if p.is_file())
else:
    from mlx_audio.stt.utils import load_model
    from huggingface_hub import snapshot_download
    model_dir = snapshot_download(args.model, local_files_only=True, allow_patterns=['*.safetensors', '*.json', '*.model', '*.txt'])
    start = time.perf_counter()
    model = load_model(args.model)
    mx.eval(model.parameters())
    mx.synchronize()
    load_s = time.perf_counter() - start
    disk_bytes = sum(p.stat().st_size for p in Path(model_dir).rglob('*') if p.is_file())
result = {'model': args.model, 'cached_cold_load_s': load_s, 'model_directory_bytes': disk_bytes, 'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'metal_peak_bytes': mx.get_peak_memory(), 'definition': 'fresh process; imports and cache resolution excluded; weights cached; evaluated parameters for MLX models'}
args.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
