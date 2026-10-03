# Decisions

Each choice, the options we weighed, and why we chose what we did.

## 1. Patch Handy instead of switching apps

| Option | For | Against |
|---|---|---|
| **Patch upstream Handy** (chosen) | Keeps Handy's interface, shortcuts, history, and every built-in model | We maintain a fork forever |
| Use the [Handy-Cloud](https://github.com/in0vik/Handy-Cloud) fork | Already has an OpenAI-compatible provider | Stuck on Handy 0.8.2; adds cloud features we do not want |
| [Spokenly](https://spokenly.app/docs/local-only-mode) | Takes a local OpenAI-compatible server; free with your own models; has an iOS app | Closed source; a different app to learn |
| [VoiceInk](https://tryvoiceink.com/docs/custom-models) | Takes a custom `/v1/audio/transcriptions` URL; open source | Custom models are batch-only; paid license |

If you do not care about Handy itself, try Spokenly or VoiceInk with the
server in this repo. You skip the fork entirely.

## 2. Keep the patch small and off by default

The patch adds one bypass at the start of `TranscriptionManager::transcribe`.
It is active only when `local-asr.json` exists. Without that file, Handy Local
is upstream Handy. We did not build a second model registry or a settings
screen. Both would double the code that conflicts on every upstream update.

## 3. Allow only `127.0.0.1`

The patch refuses any other host, disables proxies, and disables redirects.
A typo cannot send your audio to the internet. The price: one Mac cannot serve
another. To share a server across machines, relax the check in
`local_asr.rs` and accept that audio crosses your network.

## 4. Use mlx-audio for the server

| Option | For | Against |
|---|---|---|
| **mlx-audio** (chosen) | Mature; Metal-native; one process hosts many models chosen by the `model` field | Loads every model it serves; keeps freed GPU memory |
| whisper.cpp server | Mature and light | Whisper models only; different route |
| A custom FastAPI app | Full control | More code to own |

mlx-audio could not load Phonon-2's packed format, so Phonon-2 runs under
Fermion's own server. A short router in `server/launch.py` sends each
request to the right backend. `launch.py` also changes mlx-audio's default
response format to JSON at startup. An `assert` stops the server if an
mlx-audio upgrade moves that line.

## 5. Recommend Granite NAR as the final model

We measured five models on 315 clips ([results](../server/results.md)).
Granite Speech 4.1 2B NAR had the lowest WER, 4.31% against Parakeet's 5.12%.
It takes 0.51 s per dictation clip, which is still quick.

We first scored with a simple normalizer. Qwen3-ASR looked far worse than it
was, because it writes numbers and drops fillers differently from the
references. The Open ASR Leaderboard normalizer fixed most of that gap. Use it
when you compare models.

Nothing at 700 MB or less beat Parakeet v3, in published scores or in ours.

## 6. Add live preview with a second model

Batch models cannot stream. To show live text, Handy Local resends all audio so
far every 0.8 s to a fast model (Phonon-2) and shows its text in the overlay.
At stop, the final model transcribes the whole recording, and only its text
is pasted.

| For | Against |
|---|---|
| You see text while you speak | Two models in memory |
| Pasted text keeps the accurate model | Preview work is thrown away: about 250 s of audio processed for a 20 s dictation |

A better design commits each segment at pauses, so each segment runs once.
We did not build it; it adds code to maintain. True streaming models, such as
Handy's built-in Parakeet Unified, avoid the problem.

## 7. Rename the app to Handy Local

Two menu-bar apps named Handy confused us. The patch renames the product,
window, tray, overlay, and logo, and keeps the bundle ID
`com.pais.handy.local-asr`. The logo change is the riskiest part of the patch
for merge conflicts. Drop it if it gets in your way.

## 8. Our final setup

On a 32 GB laptop, we went back to official Handy with built-in Parakeet and
Apple Intelligence post-processing:

- The accuracy gain from Granite is real but small.
- Cleanup fixes the errors you notice most: punctuation, fillers, numbers.
- No fork to rebase, no server to run, no extra memory to manage.

This repo stays useful for machines with memory to spare, for models Handy
does not ship, and for sharing one model across several tools.
