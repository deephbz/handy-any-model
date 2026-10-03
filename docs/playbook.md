# Playbook

Every step to install, run, and maintain Handy Local and its server.
Requires an Apple Silicon Mac, Xcode, [Bun](https://bun.sh),
[Rust](https://rustup.rs), and [uv](https://docs.astral.sh/uv/).

## 1. Start the server

```bash
server/setup.sh     # once: venv + model downloads (about 10 GB)
server/start.sh     # serves 127.0.0.1:8178 and Phonon-2 on 127.0.0.1:8179
```

To test every model (optional; loads all five, about 12 GB of memory):

```bash
~/.cache/handy-cloud/venv/bin/python samples/prepare.py   # builds test clips, downloads LibriSpeech
python3 server/check_endpoint.py
```

`setup.sh` puts the Python environment and logs in `~/.cache/handy-cloud/`
and model weights in the Hugging Face cache. It also writes two launchd plists
into `server/`. To start the server at login, copy them to
`~/Library/LaunchAgents/` and load them with `launchctl bootstrap gui/$(id -u) <plist>`.

Check it:

```bash
curl -s 127.0.0.1:8178/v1/models
```

Stop it with `server/stop.sh`.

## 2. Build Handy Local

```bash
patches/apply.sh handy
cd handy
bun install
export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
CMAKE_POLICY_VERSION_MINIMUM=3.5 bun run tauri build --bundles app
```

The app lands at `src-tauri/target/release/bundle/macos/Handy Local.app`.
`SDKROOT` avoids a link error when Xcode and the Command Line Tools disagree.

Test the patch (optional):

```bash
CMAKE_POLICY_VERSION_MINIMUM=3.5 cargo test --release --manifest-path src-tauri/Cargo.toml local_
python3 scripts/test-local-asr-app.py
```

## 3. Configure

Create `~/Library/Application Support/com.pais.handy.local-asr/local-asr.json`:

```json
{
  "url": "http://127.0.0.1:8178/v1/audio/transcriptions",
  "model": "mlx-community/granite-speech-4.1-2b-nar-mlx-5bit",
  "preview_model": "FermionResearch/Phonon-2",
  "preview_interval_ms": 800
}
```

| Field | Meaning |
|---|---|
| `url` | Must start with `http://127.0.0.1`. Other hosts are refused. |
| `model` | Writes the pasted text. Must match an ID from `/v1/models`. |
| `preview_model` | Optional. Shows live text in the overlay. Remove it to turn the preview off. |
| `preview_interval_ms` | Optional. Time between preview updates. Default 800. |

Handy Local reads this file on every dictation. You never need to restart it.
Delete the file and Handy Local uses Handy's built-in models again.

## 4. Run

```bash
open -n --env HANDY_DISABLE_UPDATER=1 "handy/src-tauri/target/release/bundle/macos/Handy Local.app"
```

On first launch:

1. Grant Microphone and Accessibility access when macOS asks.
2. Skip the model download. Quit, set `"onboarding_completed": true` inside
   `settings` in `settings_store.json` (same folder as the config), and launch again.
3. Keep the overlay style on **Live** if you want the preview.
4. Keep post-processing off, or point it at a local LLM, so text stays local.

Press **Option+Space** to start and again to stop. Official Handy can run at the
same time if it uses a different shortcut.

## 5. Swap models

1. Pick a candidate. Check its license, size, and benchmark scores.
2. Add its ID to `MODEL_IDS` in `server/launch.py`. It must be a model mlx-audio
   can load. A model it cannot load needs its own server and a route in
   `launch.py`, as Phonon-2 has.
3. Restart: `server/stop.sh && server/start.sh`. Confirm the ID in `/v1/models`.
4. Change `model` in `local-asr.json`.
5. Dictate a known sentence. Confirm the text, and the model ID in
   `~/.cache/handy-cloud/server.log`. Keep it, or restore the old ID.

To measure a candidate against the others, see [samples/README.md](../samples/README.md)
and `server/run_comparison.sh`.

## 6. Fix problems

| Symptom | Cause and fix |
|---|---|
| Nothing pasted, server log shows `404` | Typo in `model`. Copy the ID from `/v1/models`. |
| Nothing pasted, no server request | Server down. Run `server/start.sh`. |
| Recording gets no audio | Microphone access missing, or the screen is locked. |
| The editor receives an empty paste | Raise `paste_delay_after_ms` in `settings_store.json`. We use 1000. |
| First dictation takes several seconds | The model loads on first use. Later requests are fast. |
| Mac slows down, swap grows | The server holds too much GPU memory. Restart it. Serve fewer models. |
| Settings screen names a built-in model | Cosmetic. With the config file present, dictation uses the server. |

Logs: `~/Library/Logs/com.pais.handy.local-asr/handy.log` and
`~/.cache/handy-cloud/server.log`.

## 7. Follow upstream Handy

1. Clone the new upstream commit.
2. Apply the patch. Expect conflicts in `managers/transcription.rs` and
   `actions.rs`. They are upstream's busiest files.
3. Rebuild, run the tests in step 2, and dictate once.
4. Regenerate the patch with `git diff` and record the new base commit in
   `patches/apply.sh`.

## 8. Uninstall

```bash
server/stop.sh
rm -rf ~/.cache/handy-cloud "handy" \
  "$HOME/Library/Application Support/com.pais.handy.local-asr" \
  "$HOME/Library/Logs/com.pais.handy.local-asr"
```

Model weights stay in `~/.cache/huggingface/hub`. Delete the ones you no longer want.
Official Handy and its data are untouched.
