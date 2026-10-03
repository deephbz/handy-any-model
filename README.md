# handy-any-model

Use any open-weight speech model with [Handy](https://github.com/cjpais/Handy),
the free offline dictation app. Your audio never leaves your Mac.

```text
Handy Local (patched Handy) ── POST 127.0.0.1:8178/v1/audio/transcriptions ──▶ local server
   record, paste, history                                                       any model you choose
```

Handy runs only the models in its own catalog. Its maintainer has said Handy
will not support custom transcription endpoints
([PR #1435](https://github.com/cjpais/Handy/pull/1435)). This repo adds one,
limited to `127.0.0.1`, and gives you a tested local server to put behind it.

Tested on an Apple M4 Mac with 32 GB, macOS, upstream Handy `b38987a`
(v0.9.7 plus 16 commits).

## Do you need this?

Probably not. Read this first.

| You want | Do this |
|---|---|
| Better accuracy than Parakeet | Pick **Granite Speech 4.1 2B NAR** or **Qwen3-ASR** in official Handy. Both ship in its catalog. |
| Cleaner text (punctuation, fillers, numbers) | Turn on post-processing in official Handy with **Apple Intelligence**. It runs on-device. See [docs/post-processing.md](docs/post-processing.md). |
| A model Handy does not ship, the day it is released | Use this repo. |
| One strong model shared by several apps or scripts | Use this repo. |

Our own verdict: on a laptop, official Handy with built-in Parakeet plus
Apple Intelligence cleanup is the better daily setup. This repo pays off on
a machine with memory to spare and a wish to try every new model.

## What you get

- **[patches/handy-local.patch](patches/handy-local.patch):** turns Handy into
  *Handy Local*. It sends audio to your local server when a config file exists
  and otherwise behaves exactly like Handy. It installs next to official Handy.
- **[server/](server/):** an [mlx-audio](https://github.com/Blaizzy/mlx-audio)
  server on `127.0.0.1:8178`. It routes Phonon-2 to Fermion's own server.
- **Live preview (optional):** a fast model shows text in the overlay while
  you speak. A more accurate model writes the text that gets pasted.
- **Benchmarks:** five models on 315 clips, with the scripts to rerun them.

## Results

Local run, 315 English clips: LibriSpeech test-other and AMI meeting speech.
WER uses the Open ASR Leaderboard normalizer. Latency is the warm median for a
5–7 s dictation clip.

| Model | WER | Latency | Weights on disk |
|---|---:|---:|---:|
| Granite Speech 4.1 2B NAR, MLX 5-bit | **4.31%** | 0.51 s | 2.4 GB |
| Parakeet TDT 0.6B v3, MLX F32 (baseline) | 5.12% | 0.20 s | 2.5 GB |
| Qwen3-ASR 1.7B, MLX 8-bit | 5.19% | 1.12 s | 2.5 GB |
| Phonon-2 | 5.45% | **0.13 s** | **0.18 GB** |
| Qwen3-ASR 1.7B, MLX 4-bit | 5.56% | 0.75 s | 1.6 GB |

- Granite made 16% fewer errors than Parakeet, at 2.5× the latency.
- No model at 700 MB or less beat Parakeet v3. Phonon-2 is tiny and fast, but
  less accurate.
- Qwen3-ASR leads the public leaderboard but lost here, likely to quantization.
- 315 clips is a small sample. Treat the ranking as provisional.

Full tables: [server/results.md](server/results.md). Sourced survey of 17
models: [docs/model-survey.md](docs/model-survey.md).

## Quick start

```bash
patches/apply.sh handy          # clone Handy at the tested commit, apply the patch
server/setup.sh                 # Python env + model downloads (about 10 GB)
server/start.sh                 # serve on 127.0.0.1:8178
```

Then build Handy Local and write one config file. Every step:
[docs/playbook.md](docs/playbook.md).

## Costs

Know these before you start.

- **You own a fork.** Upstream will not take this feature. Each Handy release
  you want means a rebase, a rebuild, and a retest. Handy Local never
  auto-updates.
- **Memory.** Every model you use stays loaded, at 2–3 GB each. MLX also keeps
  freed GPU memory. After a long benchmark run, our two server processes held
  29 GB. A restart brings them back to about 7 GB. Official Handy loads one
  model and unloads it when idle.
- **Wasted work in live preview.** Batch models cannot stream. The preview
  sends all audio so far every 0.8 s, then the final model transcribes it all
  again. Turn the preview off if you do not need it.

More: [docs/decisions.md](docs/decisions.md) explains each choice and its
trade-offs. [docs/architecture.md](docs/architecture.md) shows how Handy works
and what the patch changes.

## Docs

| File | Read it to |
|---|---|
| [docs/playbook.md](docs/playbook.md) | Install, run, swap models, fix problems, uninstall |
| [docs/decisions.md](docs/decisions.md) | See what we chose, what we rejected, and why |
| [docs/architecture.md](docs/architecture.md) | Learn Handy's internals and the patch |
| [docs/model-survey.md](docs/model-survey.md) | Compare open-weight English ASR models, with sources |
| [docs/post-processing.md](docs/post-processing.md) | Clean up text with a local LLM in official Handy |
| [server/results.md](server/results.md) | Read the full benchmark |

## License

MIT. The patch modifies Handy, which is MIT-licensed by CJ Pais. Model weights
keep their own licenses; check each model card before use.
