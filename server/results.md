# Local ASR comparison

Stage: exploration. Machine: Apple M4, 32 GB; macOS arm64.
Runtime: MLX Audio 0.5.6; MLX 0.32.2; Fermion 0.2.7.

**Recommended default: `mlx-community/granite-speech-4.1-2b-nar-mlx-5bit`.**
Granite NAR Q5 has the lowest normalized WER on this fixed corpus. It trades larger model files and higher latency for measured accuracy. This recommendation remains provisional. Phonon-2 is the compact alternative.

Qwen3-ASR 1.7B is the highest-ranked open model in `../docs/model-survey.md`.
That leaderboard rank does not transfer to this quantized local run.
Phonon-2 is the served compact candidate. Its download is 163.5 MB;
its unpacked model files use 177.7 MB. Compactness does not establish better accuracy.

## Accuracy

| Model | LS clean (5) | LS other (5) | Synthetic dictation (5) | LS other (200) | AMI headset (100) | All 315 clips |
|---|---:|---:|---:|---:|---:|---:|
| Parakeet v3 F32 | 0.80% | 1.52% | 2.60% | 3.37% | 10.17% | 5.75% |
| Qwen3-ASR 1.7B Q4 | 2.40% | 6.82% | 2.60% | 4.17% | 14.37% | 7.90% |
| Qwen3-ASR 1.7B Q8 | 3.20% | 6.06% | 2.60% | 3.96% | 13.57% | 7.49% |
| Phonon-2 five-value | 0.80% | 3.03% | 0.00% | 4.23% | 10.07% | 6.21% |
| Granite 4.1 2B NAR Q5 | 0.00% | 0.00% | 2.60% | 2.63% | 8.16% | 4.54% |

The table above uses the original simple normalizer. It excludes punctuation/case.
The Open ASR normalizer changes number, contraction, compound, and filler conventions.

### Open ASR Leaderboard normalization

| Model | LS other 200 | AMI 100 | All clips | Corpus edits / normalized words |
|---|---:|---:|---:|---:|
| Parakeet v3 F32 | 3.25% | 8.71% | 5.12% | 303 / 5913 |
| Qwen3-ASR 1.7B Q4 | 3.57% | 9.40% | 5.56% | 329 / 5913 |
| Qwen3-ASR 1.7B Q8 | 3.28% | 8.89% | 5.19% | 307 / 5913 |
| Phonon-2 five-value | 4.01% | 8.34% | 5.45% | 322 / 5913 |
| Granite 4.1 2B NAR Q5 | 2.54% | 7.74% | 4.31% | 255 / 5913 |

Normalizer source, verbatim WER, error categories, and ten Qwen example diffs:
`normalization.md`. Raw rescoring evidence: `normalization.json`.

Weighted simple-score corpus totals use 5,858 reference words. Set-specific edit counts:

| Model | LS other 200 edits / 3380 | AMI 100 edits / 2144 | All edits / 5858 |
|---|---:|---:|---:|
| Parakeet v3 F32 | 114 | 218 | 337 |
| Qwen3-ASR 1.7B Q4 | 141 | 308 | 463 |
| Qwen3-ASR 1.7B Q8 | 134 | 291 | 439 |
| Phonon-2 five-value | 143 | 216 | 364 |
| Granite 4.1 2B NAR Q5 | 89 | 175 | 266 |

## Latency, cached cold load, and size

| Model | Warm dictation median s | Cached cold load s | Model files MB | Load peak RSS MiB | Endpoint sampled RSS MiB | Load peak Metal MiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| Parakeet v3 F32 | 0.197 | 3.675 | 2508.9 | 2042.2 | 2827.2 | 2431.6 |
| Qwen3-ASR 1.7B Q4 | 0.750 | 4.478 | 1607.6 | 1439.5 | 2053.6 | 1534.8 |
| Qwen3-ASR 1.7B Q8 | 1.118 | 3.678 | 2467.9 | 1673.1 | 2818.4 | 2355.2 |
| Phonon-2 five-value | 0.131 | 13.233 | 177.7 | 2937.5 | 1890.6 | 1301.7 |
| Granite 4.1 2B NAR Q5 | 0.514 | 9.281 | 2375.1 | 2737.1 | 2759.4 | 2261.2 |

Cold load uses a fresh process with cached files. Imports and download time are excluded.
MLX weights are evaluated before the timer stops. Fermion uses its publisher loader.
Load peak RSS comes from macOS `getrusage`. Peak Metal allocation is separate.
Endpoint RSS uses 20 ms sampling; Phonon sums the router and Fermion processes.
Other endpoint RSS values cover the MLX process with one candidate loaded.
Do not add RSS and Metal values: their accounting can overlap.
These measurements do not establish whole-machine peak memory during inference.
All candidates completed sustained endpoint runs on this 32 GB machine.

## Warm per-clip latency

Three measured requests per smoke clip follow a warmup. Values are medians in seconds.
The five dictation clips are the primary UX metric.

| Clip | Audio s | Parakeet | Qwen Q4 | Qwen Q8 | Phonon | Granite NAR |
|---|---:|---:|---:|---:|---:|---:|---:|
| test-clean-1089-134686-0000.wav | 10.44 | 0.190 | 1.547 | 2.723 | 0.147 | 1.319 |
| test-clean-1188-133604-0000.wav | 10.72 | 0.181 | 1.265 | 2.033 | 0.159 | 0.717 |
| test-clean-121-121726-0000.wav | 8.46 | 0.148 | 0.983 | 1.265 | 0.142 | 0.661 |
| test-clean-1221-135766-0000.wav | 12.44 | 0.210 | 1.561 | 1.943 | 0.268 | 0.879 |
| test-clean-1284-1180-0000.wav | 8.12 | 0.168 | 1.174 | 1.618 | 0.225 | 0.642 |
| test-other-1688-142285-0000.wav | 15.00 | 0.242 | 1.604 | 2.178 | 0.286 | 1.083 |
| test-other-1998-15444-0000.wav | 13.31 | 0.254 | 1.579 | 2.483 | 0.243 | 1.114 |
| test-other-2033-164914-0000.wav | 9.07 | 0.375 | 1.107 | 1.761 | 0.159 | 0.907 |
| test-other-2414-128291-0001.wav | 8.44 | 0.365 | 0.849 | 1.645 | 0.172 | 0.718 |
| test-other-2609-156975-0002.wav | 10.74 | 0.362 | 1.049 | 1.724 | 0.229 | 0.930 |
| dictation-01.wav | 5.50 | 0.195 | 0.659 | 0.867 | 0.131 | 0.402 |
| dictation-02.wav | 6.08 | 0.209 | 0.777 | 1.118 | 0.134 | 0.514 |
| dictation-03.wav | 5.27 | 0.197 | 0.700 | 0.907 | 0.124 | 0.432 |
| dictation-04.wav | 6.07 | 0.194 | 0.750 | 1.360 | 0.127 | 0.590 |
| dictation-05.wav | 7.18 | 0.215 | 0.847 | 1.121 | 0.142 | 0.616 |

## Method and limits

```text
LibriSpeech tar -> fixed 200 positions excluding smoke clips -> accuracy manifest
AMI first test shard -> 5–15 s / >=8 words -> fixed 100 positions -> meeting manifest
manifests -> identical HTTP requests -> normalized references + hypotheses -> edit counts
edit counts / reference words -> set WER and weighted corpus WER
```

Selection occurs before inference. The 200 test-other clips contain 3,380 words.
The 100 AMI clips contain 2,144 words from EN2002a, EN2002b, and EN2002c.
AMI uses headset microphones. This is a small slice from three meetings;
it does not establish accuracy across meetings, speakers, accents, or live dictation.
The five synthetic clips measure latency and serve as a smoke test.
Text is lowercased; punctuation is removed; spaces are collapsed.
The original simple score retains number and disfluency differences.
The second score uses the pinned Open ASR English normalizer and its default mappings.
No statistical significance or general accuracy superiority is claimed.
Benchmark requests use language=en, response_format=json, and upstream decoding defaults.
No model-specific tuning was applied.

## Failures and fallback

- MLX Audio’s Phonon loader failed with `unsupported Phonon packed decoder layout`.
  Fermion 0.2.7 loaded the publisher profile and serves it through loopback routing.
- The package index supplied Fermion 0.1.24 without the speech server.
  The publisher’s 0.2.7 wheel URL is pinned in the dependency lock.
- Granite AR was not served. The available MLX-community conversion uses Granite NAR.
  The NAR Q5 model is the accuracy fallback. Do not assign it the AR leaderboard score.
- No verified <=700 MB model is clearly more accurate than Parakeet v3 in the survey.
  The compact candidate is a size trade-off.

## Runtime verification and reproduction

All five IDs returned text from `POST http://127.0.0.1:8178/v1/audio/transcriptions`.
Responses and statuses: `endpoint-checks.json`. Model listing: `GET /v1/models`.
The server logs model IDs and filenames. Both listeners bind only 127.0.0.1.
Serving runs offline. Neither launchd plist is loaded.
Raw evidence: `benchmarks/*-{smoke,accuracy,meeting,load}.json`.
The raw rows preserve references, hypotheses, edit counts, all timings, and runtime versions.
Model revisions, file sizes, and the Phonon archive hash: `model-artifacts.json`.
An independent Levenshtein implementation confirmed all five normalized edit totals.
`baseline.json` preserves the initial baseline endpoint acceptance run.
Source selection and licenses: `../samples/README.md`. Commands: `README.md`.
