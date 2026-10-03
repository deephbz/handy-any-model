# Fixed ASR smoke-test corpus

Scope: quick local model comparisons; no population accuracy claims.
`manifest.json` owns the reference text, provenance, clip IDs, and durations.
All WAV files use 16 kHz mono signed 16-bit PCM.
The original manifest has 15 smoke clips. Two accuracy manifests add 300 clips.

- Five test-clean clips and five test-other clips come from LibriSpeech.
  `prepare.py` selects the first 5–15 second clip from each of five speakers
  in sorted archive order. Selection does not use recognition results.
- Five dictation-style clips use macOS Samantha speech at 130 words/minute.
  The files include 0.5 seconds of trailing silence. They are synthetic.
  They do not measure live microphone accuracy.

LibriSpeech source and CC BY 4.0 license: https://www.openslr.org/12
The original recordings derive from LibriVox public-domain audiobooks.
Archives stay under `~/.cache/handy-cloud/audio/`.

## Accuracy sets

`prepare_accuracy.py` selects 200 test-other utterances at evenly spaced positions
in sorted transcript order. It excludes the five smoke clips. It does not filter
by recognition results. `accuracy-manifest.json` records 3,380 reference words.

`prepare_meeting.py` selects 100 AMI headset test clips from the first public test
Parquet shard. It filters for 5–15 seconds and at least eight reference words.
It then selects evenly spaced positions. `meeting-manifest.json` records
2,144 reference words, row indices, speakers, and meeting IDs.
The slice contains EN2002a, EN2002b, and EN2002c. It is not the full AMI test set.

AMI source and CC BY 4.0 license:
https://huggingface.co/datasets/edinburghcstr/ami
Underlying corpus: https://groups.inf.ed.ac.uk/ami/corpus/
The public shard stays in `~/.cache/handy-cloud/audio/`.

`benchmark.py` lowercases text, removes punctuation, and collapses spaces.
It does not expand numbers. It reports corpus WER from summed edit counts.
A 20 ms sampler measures process RSS. RSS is not total Apple unified-memory use.
The script records the first hypothesis and all repeated hypotheses.
Latency includes multipart upload, inference, and the local HTTP response.
