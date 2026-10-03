"""Render comparison tables from final raw benchmark records; do not infer untested accuracy."""
import argparse
import json
from pathlib import Path
import statistics

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--default', default='granite', choices=['parakeet', 'qwen4', 'qwen8', 'phonon', 'granite'])
parser.add_argument('--reason', default='Granite NAR Q5 has the lowest normalized WER on this fixed corpus. It trades larger model files and higher latency for measured accuracy. This recommendation remains provisional. Phonon-2 is the compact alternative.')
args = parser.parse_args()
keys = ['parakeet', 'qwen4', 'qwen8', 'phonon', 'granite']
names = {'parakeet': 'Parakeet v3 F32', 'qwen4': 'Qwen3-ASR 1.7B Q4', 'qwen8': 'Qwen3-ASR 1.7B Q8', 'phonon': 'Phonon-2 five-value', 'granite': 'Granite 4.1 2B NAR Q5'}
def read(key, kind):
    return json.loads((here / 'benchmarks' / f'{key}-{kind}.json').read_text())
records = {k: {kind: read(k, kind) for kind in ['smoke', 'accuracy', 'meeting', 'load']} for k in keys}
normalization = json.loads((here / 'normalization.json').read_text())
normalized = {m['key']: m for m in normalization['models']}
assert all(len(normalized[k]['rows']) == 315 for k in keys)
lines = ['# Local ASR comparison', '', 'Stage: exploration. Machine: Apple M4, 32 GB; macOS arm64.', 'Runtime: MLX Audio 0.5.6; MLX 0.32.2; Fermion 0.2.7.', '', f"**Recommended default: `{records[args.default]['smoke']['model']}`.**", args.reason, '', 'Qwen3-ASR 1.7B is the highest-ranked open model in `../docs/models.md`.', 'That leaderboard rank does not transfer to this quantized local run.', 'Phonon-2 is the served compact candidate. Its download is 163.5 MB;', 'its unpacked model files use 177.7 MB. Compactness does not establish better accuracy.', '', '## Accuracy', '', '| Model | LS clean (5) | LS other (5) | Synthetic dictation (5) | LS other (200) | AMI headset (100) | All 315 clips |', '|---|---:|---:|---:|---:|---:|---:|']
summary = {'recommended_model': records[args.default]['smoke']['model'], 'reason': args.reason, 'models': []}
for key in keys:
    d = records[key]
    smoke = d['smoke']
    per = smoke['per_set']
    datasets = [smoke, d['accuracy'], d['meeting']]
    words = sum(x['reference_words'] for x in datasets)
    errors = sum(x['errors'] for x in datasets)
    values = [per[g]['wer'] for g in ['test-clean', 'test-other', 'synthetic-dictation']] + [d['accuracy']['wer'], d['meeting']['wer'], errors / words]
    lines.append('| ' + names[key] + ' | ' + ' | '.join(f'{v:.2%}' for v in values) + ' |')
    load = d['load']
    dictation = [r for r in smoke['rows'] if r['group'] == 'synthetic-dictation']
    summary['models'].append({'key': key, 'model': smoke['model'], 'corpus_errors': errors, 'corpus_reference_words': words, 'corpus_wer': errors / words, 'real_accuracy_wer': (d['accuracy']['errors'] + d['meeting']['errors']) / (d['accuracy']['reference_words'] + d['meeting']['reference_words']), 'dictation_warm_median_s': statistics.median(r['median_latency_s'] for r in dictation), 'endpoint_peak_sampled_rss_bytes': max(x['peak_sampled_rss_bytes'] for x in datasets), **{k:v for k,v in load.items() if k!='model'}})
lines += ['', 'The table above uses the original simple normalizer. It excludes punctuation/case.', 'The Open ASR normalizer changes number, contraction, compound, and filler conventions.', '', '### Open ASR Leaderboard normalization', '', '| Model | LS other 200 | AMI 100 | All clips | Corpus edits / normalized words |', '|---|---:|---:|---:|---:|']
for key, s in zip(keys, summary['models']):
    n = normalized[key]
    total = n['total']['leaderboard']
    s['leaderboard_wer'] = total['wer']
    s['leaderboard_errors'] = total['errors']
    s['leaderboard_reference_words'] = total['words']
    lines.append(f"| {names[key]} | {n['per_set']['test-other-200']['leaderboard']['wer']:.2%} | {n['per_set']['ami-ihm-100']['leaderboard']['wer']:.2%} | {total['wer']:.2%} | {total['errors']} / {total['words']} |")
lines += ['', 'Normalizer source, verbatim WER, error categories, and ten Qwen example diffs:', '`normalization.md`. Raw rescoring evidence: `normalization.json`.', '', 'Weighted simple-score corpus totals use 5,858 reference words. Set-specific edit counts:', '', '| Model | LS other 200 edits / 3380 | AMI 100 edits / 2144 | All edits / 5858 |', '|---|---:|---:|---:|']
for key, s in zip(keys, summary['models']):
    d = records[key]
    lines.append(f"| {names[key]} | {d['accuracy']['errors']} | {d['meeting']['errors']} | {s['corpus_errors']} |")
lines += ['', '## Latency, cached cold load, and size', '', '| Model | Warm dictation median s | Cached cold load s | Model files MB | Load peak RSS MiB | Endpoint sampled RSS MiB | Load peak Metal MiB |', '|---|---:|---:|---:|---:|---:|---:|---:|']
for key, s in zip(keys, summary['models']):
    lines.append(f"| {names[key]} | {s['dictation_warm_median_s']:.3f} | {s['cached_cold_load_s']:.3f} | {s['model_directory_bytes']/1e6:.1f} | {s['process_peak_rss_bytes']/2**20:.1f} | {s['endpoint_peak_sampled_rss_bytes']/2**20:.1f} | {s['metal_peak_bytes']/2**20:.1f} |")
lines += ['', 'Cold load uses a fresh process with cached files. Imports and download time are excluded.', 'MLX weights are evaluated before the timer stops. Fermion uses its publisher loader.', 'Load peak RSS comes from macOS `getrusage`. Peak Metal allocation is separate.', 'Endpoint RSS uses 20 ms sampling; Phonon sums the router and Fermion processes.', 'Other endpoint RSS values cover the MLX process with one candidate loaded.', 'Do not add RSS and Metal values: their accounting can overlap.', 'These measurements do not establish whole-machine peak memory during inference.', 'All candidates completed sustained endpoint runs on this 32 GB machine.', '', '## Warm per-clip latency', '', 'Three measured requests per smoke clip follow a warmup. Values are medians in seconds.', 'The five dictation clips are the primary UX metric.', '', '| Clip | Audio s | Parakeet | Qwen Q4 | Qwen Q8 | Phonon | Granite NAR |', '|---|---:|---:|---:|---:|---:|---:|---:|']
for i, row in enumerate(records['parakeet']['smoke']['rows']):
    timing = [records[k]['smoke']['rows'][i]['median_latency_s'] for k in keys]
    assert all(records[k]['smoke']['rows'][i]['file'] == row['file'] for k in keys)
    lines.append(f"| {row['file']} | {row['duration_s']:.2f} | " + ' | '.join(f'{v:.3f}' for v in timing) + ' |')
lines += ['', '## Method and limits', '', '```text', 'LibriSpeech tar -> fixed 200 positions excluding smoke clips -> accuracy manifest', 'AMI first test shard -> 5–15 s / >=8 words -> fixed 100 positions -> meeting manifest', 'manifests -> identical HTTP requests -> normalized references + hypotheses -> edit counts', 'edit counts / reference words -> set WER and weighted corpus WER', '```', '', 'Selection occurs before inference. The 200 test-other clips contain 3,380 words.', 'The 100 AMI clips contain 2,144 words from EN2002a, EN2002b, and EN2002c.', 'AMI uses headset microphones. This is a small slice from three meetings;', 'it does not establish accuracy across meetings, speakers, accents, or live dictation.', 'The five synthetic clips measure latency and serve as a smoke test.', 'Text is lowercased; punctuation is removed; spaces are collapsed.', 'The original simple score retains number and disfluency differences.', 'The second score uses the pinned Open ASR English normalizer and its default mappings.', 'No statistical significance or general accuracy superiority is claimed.', 'Benchmark requests use language=en, response_format=json, and upstream decoding defaults.', 'No model-specific tuning was applied.', '', '## Failures and fallback', '', '- MLX Audio’s Phonon loader failed with `unsupported Phonon packed decoder layout`.', '  Fermion 0.2.7 loaded the publisher profile and serves it through loopback routing.', '- The package index supplied Fermion 0.1.24 without the speech server.', '  The publisher’s 0.2.7 wheel URL is pinned in the dependency lock.', '- Granite AR was not served. The available MLX-community conversion uses Granite NAR.', '  The NAR Q5 model is the accuracy fallback. Do not assign it the AR leaderboard score.', '- No verified <=700 MB model is clearly more accurate than Parakeet v3 in the survey.', '  The compact candidate is a size trade-off.', '', '## Runtime verification and reproduction', '', 'All five IDs returned text from `POST http://127.0.0.1:8178/v1/audio/transcriptions`.', 'Responses and statuses: `endpoint-checks.json`. Model listing: `GET /v1/models`.', 'The server logs model IDs and filenames. Both listeners bind only 127.0.0.1.', 'Serving runs offline. Neither launchd plist is loaded.', 'Raw evidence: `benchmarks/*-{smoke,accuracy,meeting,load}.json`.', 'The raw rows preserve references, hypotheses, edit counts, all timings, and runtime versions.', 'Model revisions, file sizes, and the Phonon archive hash: `model-artifacts.json`.', 'An independent Levenshtein implementation confirmed all five normalized edit totals.', '`baseline.json` preserves the initial baseline endpoint acceptance run.', 'Source selection and licenses: `../samples/README.md`. Commands: `README.md`.']
(here / 'comparison-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(here / 'results.md').write_text('\n'.join(lines) + '\n')
