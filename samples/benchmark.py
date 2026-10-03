"""Measure endpoint WER, warm request latency, and sampled server RSS on the fixed corpus."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import statistics
import threading
import time

import jiwer
import psutil
import requests

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--manifest', type=Path, default=HERE / 'manifest.json')
parser.add_argument('--model', default='mlx-community/parakeet-tdt-0.6b-v3')
parser.add_argument('--url', default='http://127.0.0.1:8178/v1/audio/transcriptions')
parser.add_argument('--pid', type=int, default=int((Path.home() / '.cache/handy-cloud/server.pid').read_text()))
parser.add_argument('--extra-pid', type=int, action='append', default=[])
parser.add_argument('--repeats', type=int, default=3)
parser.add_argument('--output', type=Path, default=HERE.parent / 'server/baseline.json')
args = parser.parse_args()
manifest = json.loads(args.manifest.read_text())
normalize = jiwer.Compose([jiwer.ToLowerCase(), jiwer.RemovePunctuation(), jiwer.RemoveMultipleSpaces(), jiwer.Strip()])
session = requests.Session()
session.trust_env = False
peak = [0]
stop = threading.Event()
processes = [psutil.Process(pid) for pid in [args.pid, *args.extra_pid]]
def sample():
    while not stop.is_set():
        try:
            peak[0] = max(peak[0], sum(proc.memory_info().rss for proc in processes))
        except psutil.NoSuchProcess:
            break
        stop.wait(0.02)
thread = threading.Thread(target=sample, daemon=True)
thread.start()
def transcribe(row):
    with (HERE / row['file']).open('rb') as audio:
        start = time.perf_counter()
        response = session.post(args.url, files={'file': (row['file'], audio, 'audio/wav')}, data={'model': args.model, 'language': 'en', 'response_format': 'json'}, timeout=300)
        response.raise_for_status()
        payload = response.json()
        assert isinstance(payload.get('text'), str), payload
        return payload['text'], time.perf_counter() - start
try:
    _, first_request_s = transcribe(manifest[0])
    rows = []
    for row in manifest:
        runs = [transcribe(row) for _ in range(args.repeats)]
        reference = normalize(row['reference'])
        hypothesis = normalize(runs[0][0])
        words = jiwer.process_words(reference, hypothesis)
        rows.append({**row, 'hypothesis': runs[0][0], 'normalized_reference': reference, 'normalized_hypothesis': hypothesis, 'wer': words.wer, 'substitutions': words.substitutions, 'deletions': words.deletions, 'insertions': words.insertions, 'reference_words': len(reference.split()), 'latencies_s': [r[1] for r in runs], 'median_latency_s': statistics.median(r[1] for r in runs), 'repeat_hypotheses': [r[0] for r in runs]})
        print(row['file'], f'WER={words.wer:.3f}', f'{rows[-1]["median_latency_s"]:.3f}s', flush=True)
finally:
    stop.set()
    thread.join()
errors = sum(r['substitutions'] + r['deletions'] + r['insertions'] for r in rows)
words = sum(r['reference_words'] for r in rows)
result = {'created_at': datetime.now(timezone.utc).isoformat(), 'model': args.model, 'endpoint': args.url, 'platform': platform.platform(), 'versions': {p: importlib.metadata.version(p) for p in ('mlx-audio', 'mlx', 'jiwer')}, 'normalization': 'lowercase; remove punctuation; collapse spaces; strip; no number expansion', 'warmup_request_s': first_request_s, 'peak_sampled_rss_bytes': peak[0], 'rss_sampling_interval_s': 0.02, 'wer': errors / words, 'errors': errors, 'reference_words': words, 'rows': rows}
args.output.parent.mkdir(parents=True, exist_ok=True)
result['manifest'] = str(args.manifest.relative_to(HERE.parent)) if args.manifest.is_relative_to(HERE.parent) else str(args.manifest)
result['rss_processes'] = [args.pid, *args.extra_pid]
result['per_set'] = {}
for group in sorted({r['group'] for r in rows}):
    group_rows = [r for r in rows if r['group'] == group]
    group_errors = sum(r['substitutions'] + r['deletions'] + r['insertions'] for r in group_rows)
    group_words = sum(r['reference_words'] for r in group_rows)
    result['per_set'][group] = {'errors': group_errors, 'reference_words': group_words, 'wer': group_errors / group_words}
args.output.write_text(json.dumps(result, indent=2) + '\n')
print(f'Aggregate WER: {errors}/{words} = {errors / words:.2%}; peak sampled RSS: {peak[0] / 2**20:.1f} MiB')
