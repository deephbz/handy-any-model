# Architecture

How Handy works, and what the patch changes.

## Handy

Handy is a [Tauri](https://tauri.app) app. A Rust process does the work. A
React web view draws the settings window and the recording overlay, and calls
Rust through typed commands (`src/bindings.ts`).

```text
Rust (src-tauri/src)                                      React (src/)
──────────────────────────────────────────────────        ─────────────
shortcut/ ─ key press ─▶ actions.rs  TranscribeAction       settings window
                            │                                    ▲
managers/audio.rs + audio_toolkit/   mic → 16 kHz → VAD          │ commands
                            │ samples                            │
                            ▼                                    │
managers/transcription.rs  TranscriptionManager ◀─ managers/model.rs + catalog/catalog.json
   ├─ engines: transcribe.cpp (GGUF on Metal), ONNX
   ├─ stream worker ─ StreamTextEvent ─▶ overlay (live text)
   └─ final text
                            ▼
clipboard.rs, input.rs     paste into the focused app
managers/history.rs        SQLite + WAV history
settings.rs                settings_store.json
```

Familiar features, in code:

- **Models screen:** `catalog.json` and `ModelManager`. The speed and accuracy
  bars are fixed scores in that file, not measurements on your Mac.
- **Live overlay:** the stream worker in `TranscriptionManager`.
- **Idle unload:** a watcher thread in `TranscriptionManager`.
- **Post-processing:** `actions.rs` and `llm_client.rs`. See
  [post-processing.md](post-processing.md).

## The patch

```text
TranscribeAction
  └─ TranscriptionManager::transcribe(audio)
       ├─ local-asr.json exists? ── yes ─▶ local_asr::Config::transcribe ─▶ POST 127.0.0.1
       └─ no ─▶ upstream engines (unchanged)

recording, if preview_model is set and overlay is Live
  └─ local_preview::PreviewBuffer ─ every 0.8 s, one request at a time ─▶ StreamTextEvent
```

| Part | Files | Merge risk |
|---|---|---|
| HTTP engine: reads config, checks the host, builds WAV, parses `{text}` | `local_asr.rs` (new) | Low |
| Preview timer: 30 s audio cap, one request in flight | `local_preview.rs` (new) | Low |
| Hooks: skip model loading, call the engine, run the preview | `managers/transcription.rs`, `actions.rs`, `lib.rs` | **High** |
| HTTP client features `blocking`, `multipart` | `Cargo.toml` | Low |
| Bundle ID `com.pais.handy.local-asr`; no updater artifacts | `tauri.conf.json` | Low |
| Name "Handy Local" | `tray.rs`, `overlay.rs`, `cli.rs`, `index.html`, `i18n/localAppName.ts`, `HandyTextLogo.tsx` | Medium |
| Tests | `local_asr.rs`, `local_preview.rs`, `scripts/test-local-asr-app.py` | Low |

The new bundle ID gives Handy Local its own settings, history, logs, and macOS
permissions. It never touches official Handy's data.

## The server

```text
:8178  server/launch.py  (mlx-audio + router)
         ├─ GET  /v1/models                 → MODEL_IDS
         ├─ POST /v1/audio/transcriptions   model = Phonon-2 → :8179 fermion serve
         └─                                 any other ID    → mlx-audio
```

- mlx-audio loads a model on its first request and keeps it loaded.
- Both servers bind `127.0.0.1` only and run with `HF_HUB_OFFLINE=1`.
- `start.sh` and `stop.sh` record PIDs in `~/.cache/handy-cloud/`.

## Maintenance

| Item | Work | When |
|---|---|---|
| Upstream Handy | Rebase the patch, rebuild, retest | Each release you want |
| macOS permissions | Re-grant Microphone or Accessibility if a rebuild resets them | Some rebuilds |
| mlx-audio upgrades | Rerun `check_endpoint.py`; fix `launch.py` if its `assert` fires | When a new model needs it |
| New models | Add the ID to `MODEL_IDS`, restart, edit config | Monthly |
| Memory | Restart the server after heavy use | As needed |
| Each Mac | Its own server, venv, and weights | Per machine |
