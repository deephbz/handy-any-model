---
purpose: Explain local LLM dictation cleanup options in Handy.
scope: Source and upstream evidence only. No app launch, settings change, or local model benchmark.
status: Exploration; model suitability and endpoint interoperability remain provisional.
---

# Local post-processing in Handy

Checked on 2026-10-03.

## Result

**Handy can already keep LLM cleanup on-device.** Select Apple Intelligence, or use Custom with a local OpenAI-compatible chat server. Apple Intelligence calls Apple's system model directly. Custom needs a separately managed server. Handy does not bundle a selectable open-weight text-model runner in the checked release. Sources: `handy/src-tauri/src/settings.rs:729-758`, `handy/src-tauri/src/actions.rs:199-233`, and the [tagged provider definitions][settings-tag].

**The historic `reasoning_effort: "none"` rejection has a fallback in this release.** Handy retries a rejected request without reasoning fields and remembers a successful fallback. Sources: `handy/src-tauri/src/llm_client.rs:411-451`; [merged fix #1809][pr1809].

**A bundled local LLM is an upstream direction, not a released commitment with a date or chosen model.** The maintainer wants a local-only app, but later says packaging and app stability take priority. Sources: [discussion #1581][d1581] and [discussion #847][d847].

### Source boundary

The inspected checkout is `v0.9.7-16-gb38987a` plus this repo's patch. Its upstream HEAD is `b38987a9075e62baafef11263cf8b7448dc38b51`. The release tag resolves to `05e0aedd2906f0d82722735f930465950c476b90`.

`handy/...` `file:line` pointers below refer to that checkout. I compared the relevant code with `git show v0.9.7:<path>`. The LLM client, Rust Apple bridge, Swift bridge, build script, and post-processing UI are unchanged from the tag. Settings line numbers moved after unrelated changes. The LLM processing block in actions retains the tagged behavior. This report does not treat this repo's ASR patch as a release feature. The [tagged settings][settings-tag], [actions][actions-tag], and [LLM client][client-tag] are the upstream anchors.

## How cleanup runs

```text
post-processing shortcut
  -> record -> ASR transcript
  -> selected prompt + selected provider/model
     +-> Apple Intelligence: Rust FFI -> Swift system model
     +-> HTTP provider: POST base_url/chat/completions
  -> cleaned text or original transcript on failure
  -> history -> paste
```

| Observation | Local source pointer |
|---|---|
| Post-processing defaults to disabled. Enabling it makes its settings section and shortcut available. It does not change the normal transcription action into an LLM action. | `handy/src-tauri/src/settings.rs:654-670`; `handy/src/components/Sidebar.tsx:60-64`; `handy/src-tauri/src/shortcut/handy_keys.rs:431-441`; `handy/src-tauri/src/actions.rs:867-875` |
| The macOS default shortcut is **Option+Shift+Space**. It invokes `transcribe_with_post_process`. The binding is configurable. | `handy/src-tauri/src/settings.rs:902-918`; `handy/src/components/settings/post-processing/PostProcessingSettings.tsx:430-437` |
| The dedicated action sets `post_process: true`; normal transcription sets it to false. | `handy/src-tauri/src/actions.rs:867-875` |
| Empty/whitespace transcripts skip the LLM. Missing provider, model, selected prompt, or nonempty prompt also skips it. | `handy/src-tauri/src/actions.rs:121-176` |
| The cleaned output replaces `final_text` only when processing returns `Some`. Failures retain the ASR transcript. The code stores the processed text and prompt with the history entry. | `handy/src-tauri/src/actions.rs:353-385, 733-740` |
| The app pastes `final_text` after processing. | `handy/src-tauri/src/actions.rs:745-768` |

### Prompt and request

The built-in **Improve Transcriptions** prompt wraps `${output}` in `<transcript>` tags. It asks the model to fix spelling, capitalization, punctuation, numbers, spoken punctuation, and filler words. It asks the model to preserve meaning, word order, and language. It says not to follow instructions inside the transcript, answer questions, or add an empty-transcript message. Source: `handy/src-tauri/src/settings.rs:789-795` ([tagged prompt][settings-tag]). These are model instructions. They are not a deterministic guarantee against rewriting or instruction injection.

Custom has `supports_structured_output: false`. Handy replaces `${output}` with the transcript and sends the whole result as a **user message**. Source: `handy/src-tauri/src/settings.rs:750-758`; `handy/src-tauri/src/actions.rs:311-321`; `handy/src-tauri/src/llm_client.rs:298-316, 350-360`.

Structured-output providers get a separate system prompt and user transcript. Handy removes `${output}` from the system prompt. It requests a JSON object with a `transcription` string. On a structured API error it tries the legacy prompt path. Apple Intelligence takes its own native branch. Sources: `handy/src-tauri/src/actions.rs:84-86, 193-309`.

The HTTP client appends `/chat/completions` to the base URL, sends `model`, `messages`, and `stream: false`, and reads `choices[0].message.content`. Model discovery requests `/models`. Empty API keys omit authentication headers; nonempty keys normally become bearer tokens. Sources: `handy/src-tauri/src/llm_client.rs:141-178, 329-395, 466-491`.

**Configuration implication:** enter the base URL through `/v1`, not a complete `/chat/completions` URL. The settings UI exposes Custom's base URL, API key, model selector, model refresh, and manual model creation. Sources: `handy/src/components/settings/post-processing/PostProcessingSettings.tsx:55-138`.

## Which providers stay on-device?

The preset list contains OpenAI, Z.AI, OpenRouter, Anthropic, Groq, Cerebras, Apple Intelligence on macOS ARM64, AWS Bedrock Mantle, and Custom. Only Custom allows base-URL editing. Sources: `handy/src-tauri/src/settings.rs:672-760` ([tagged definitions][settings-tag]).

| Path | Observed behavior | Locality condition |
|---|---|---|
| Apple Intelligence | Uses `apple-intelligence://local` as a marker; calls native Swift APIs instead of HTTP. | Supported device, OS, model readiness, and a real bridge build. |
| Custom + Ollama | Default base URL is `http://localhost:11434/v1`; Ollama documents this OpenAI chat API [O]. | Select a downloaded local model. A localhost client alone does not prove that the server never forwards to a cloud model. |
| Custom + LM Studio | LM Studio documents `http://localhost:1234/v1`, chat completions, and model listing [LM]. | Load a local model and keep inference local. Source-backed integration path; not tested with Handy here. |
| Custom + mlx-lm | `mlx_lm.server` documents a localhost server on port **8080** and `/v1/chat/completions` [MLX]. Base URL: `http://127.0.0.1:8080/v1`. | Use a supported local MLX checkpoint and a loopback bind. Source-backed integration path; not tested here. |
| Other presets | Their default base URLs are external HTTPS services. | They send transcript text off-device when used. Local ASR does not make remote cleanup local. |

This survey changed no settings and started no servers. The ASR server in this repo does not automatically implement text chat. Cleanup needs the chat-completions contract above.

### Apple Intelligence requirements and limitations

- **Hardware:** Handy compiles this path for macOS ARM64. Apple's device requirements include Mac with **M1 or later** [A]. An M4 meets the hardware class. Sources: `handy/src-tauri/src/settings.rs:729-739`; `handy/src-tauri/src/actions.rs:201-234`.
- **OS:** Handy's Swift bridge requires **macOS 26 or newer**. Apple's general Intelligence product requirements are separate and change across OS releases. Do not infer that earlier OS support for Writing Tools also supplies this bridge. Source: `handy/src-tauri/swift/apple_intelligence.swift:5-9, 38-50, 64-77`.
- **Readiness:** Apple Intelligence must be enabled, its model must be ready, and language/region must be supported. Apple documents device and Siri language requirements [A]; Foundation Models exposes model availability and unavailable reasons [AF]. Handy asks `SystemLanguageModel.default.availability` at use time and skips cleanup when unavailable. Source: `handy/src-tauri/swift/apple_intelligence.swift:38-50`; `handy/src-tauri/src/actions.rs:203-208`.
- **Build:** An app built with the stub bridge cannot use Apple Intelligence even on eligible hardware. The build script falls back to stubs if FoundationModels or the needed compiler support is absent. The stub reports unavailable. Sources: `handy/src-tauri/build.rs:417-459`; `handy/src-tauri/swift/apple_intelligence_stub.swift:9-25`. Full Xcode is the normal supported build path; these checks concern the developer build, not a need for end users to install Xcode.
- **On-device inference:** Apple's `SystemLanguageModel` documentation describes the on-device text foundation model [AF]. Handy constructs a `LanguageModelSession` with that model. It first requests generated `CleanedTranscript`, then falls back to plain text generation. Source: `handy/src-tauri/swift/apple_intelligence.swift:94-111`. This path does not call an external OpenAI provider or Private Cloud Compute API in the inspected code.
- **Output limit:** The value passed as `max_tokens` is applied **after generation** as a whitespace-separated word cap. It does not set a generation-token budget. Source: `handy/src-tauri/swift/apple_intelligence.swift:25-35, 80, 114-116`. The Rust action parses the provider's model field as this integer. Source: `handy/src-tauri/src/actions.rs:210-217`.

## Known bugs and their current status

| Evidence | What it establishes | Status in the checked release |
|---|---|---|
| [PR #1221][pr1221], merged | Custom began sending `reasoning_effort: "none"` to reduce thinking latency in Ollama. Later comments report a strict proxy rejecting that value. The author's timings are reports from their environment, not benchmarks on this Mac. | Historical cause. Do not assume the original one-field implementation is still the full behavior. |
| [PR #1350][pr1350], closed **without merge** | Proposed restoring a Disable reasoning toggle. Maintainer's closing comment prefers automatic fallback instead of more UI. | The proposed toggle is not evidence of a shipped setting. |
| [PR #1368][pr1368], closed **without merge** | Proposed omitting `reasoning_effort` for Custom URLs at DeepSeek. Maintainer preferred a broader automatic fix. | Do not describe this unmerged special case as the release implementation. |
| [PR #1809][pr1809], merged | Adds retry without reasoning parameters. Local tag history includes this fix. | Present. The tagged source confirms behavior independently of the PR description. |

### What the current client actually does

Source: `handy/src-tauri/src/actions.rs:188-191`; `handy/src-tauri/src/llm_client.rs:57-92, 373-451` ([tagged client][client-tag]).

```text
Custom or OpenRouter asks to disable reasoning
  DeepSeek hostname -> thinking: {type: "disabled"}
  OpenRouter id     -> reasoning: {effort: "none", exclude: true}
  other endpoint    -> reasoning_effort: "none"

HTTP 400 or 422 with reasoning fields
  -> retry once without those fields
  -> if retry succeeds: remember base_url + model until process exit
```

Residual limits from code inspection:

- The retry reacts to **any** HTTP 400/422 while reasoning fields are present. It does not prove that reasoning caused the rejection. The cache records only a successful retry. A failing retry does not disable future attempts. Source: `handy/src-tauri/src/llm_client.rs:411-451`.
- Removing a rejected field can restore compatibility but re-enable a backend's default thinking mode. Low latency remains unverified. This is **provisional inference** from the retry behavior.
- Handy strips a leading closed `<think>...</think>` block. It does not strip an unclosed block, a mid-sentence block, or every provider-specific thinking format. Source: `handy/src-tauri/src/actions.rs:70-81`.
- A malformed structured response, or JSON missing the `transcription` field, can return raw content for pasting. A successful HTTP response is not proof of safe cleanup. Source: `handy/src-tauri/src/actions.rs:268-294`.
- The Custom request exposes no temperature, context-length, or per-request generation-limit field in `ChatCompletionRequest`. Configure those controls in the local server or model configuration if needed. Source: `handy/src-tauri/src/llm_client.rs:113-123`.

The PR comments' statements about which values belong to the OpenAI specification describe their historical context. They are not a current universal API specification. Backend acceptance varies by provider and model.

## Upstream plan for bundled inference

- In [#1581][d1581], the maintainer says they are working on local LLMs. They describe an eventual local-only app and removal of third-party provider support. They require broad machine compatibility and strong model quality. This is a maintainer direction, not an implementation or migration schedule.
- In [#847][d847], the maintainer discusses a shared wrapper for heterogeneous engines such as MLX and llama.cpp. A later comment says direct app integration is a longer-term packaging project and is not the current priority. Contributors' proposed prototypes do not establish an accepted design.
- **Bounded observation:** the checked source supplies native Apple system-model inference and external HTTP providers. It supplies no bundled open-weight text-model downloader and embedded LLM engine in this post-processing path. A transcribe.cpp ASR GGUF catalog is not a text-LLM catalog.

## Small open-weight instruct candidates

These are candidates for short English dictation cleanup, not ranked winners. All have downloadable instruction-tuned/chat weights. The sizes below are the Ollama publisher's displayed **Q4_K_M artifact sizes**, not peak memory. They exclude runtime and cache overhead. A 32 GB M4 should have room for these small artifacts alongside ASR, but this is **provisional inference**. No cleanup accuracy or latency test ran here.

| Model | Published size and license | Documented runtime | Provisional role / caution |
|---|---|---|---|
| Qwen2.5-1.5B-Instruct | **1.5B** label; **986 MB** Q4_K_M [Q25O]. **Apache-2.0** [Q25]. | Ollama `qwen2.5:1.5b` [Q25O]; local chat via [O]. | Simple non-reasoning baseline. Its instruction tuning and small size justify testing it first; cleanup quality is not established. |
| Qwen3-1.7B | **1.7B** label; **1.4 GB** Q4_K_M [Q3O]. **Apache-2.0** [Q3]. | Ollama `qwen3:1.7b` [Q3O]. | More recent small chat candidate. Ensure thinking is actually disabled. Qwen documents `/no_think` for prompt-based non-thinking mode [Q3]; this is relevant if the server ignores request controls. |
| Gemma 3 1B IT | **1B** label; **815 MB** Q4_K_M [GO]. **Gemma Terms of Use**, with use restrictions [GL]. | Ollama `gemma3:1b` [GO]. | Compact text-only candidate. Small capacity may lose names, negation, or formatting instructions. This is open-weight, not Apache/MIT-licensed. |
| Llama 3.2 3B Instruct | **3B** label; **2.0 GB** Q4_K_M [LO]. **Llama 3.2 Community License** plus acceptable-use policy [LL]. | Ollama `llama3.2:3b` [LO]. | Larger comparison for instruction following and rewriting. Preserve literal meaning and test against over-editing. This is open-weight with a custom license. |

**Suggested evaluation, not an app change:** compare original ASR text with cleaned output on names, numbers, negation, questions, spoken punctuation, and text containing instructions. Count unwanted changes as failures. Check warm latency and cold-load time separately. A model that improves punctuation while deleting a negation is unsuitable for dictation cleanup.

## External sources

Primary sources were read through source code, GitHub API/HTML, and publisher pages. The LM Studio page denied direct retrieval; its first-party page was located through web search. Interoperability remains untested for all servers in this report.

[settings-tag]: https://github.com/cjpais/Handy/blob/v0.9.7/src-tauri/src/settings.rs#L632-L773
[actions-tag]: https://github.com/cjpais/Handy/blob/v0.9.7/src-tauri/src/actions.rs#L121-L344
[client-tag]: https://github.com/cjpais/Handy/blob/v0.9.7/src-tauri/src/llm_client.rs#L57-L491
[pr1221]: https://github.com/cjpais/Handy/pull/1221
[pr1350]: https://github.com/cjpais/Handy/pull/1350
[pr1368]: https://github.com/cjpais/Handy/pull/1368
[pr1809]: https://github.com/cjpais/Handy/pull/1809
[d847]: https://github.com/cjpais/Handy/discussions/847
[d1581]: https://github.com/cjpais/Handy/discussions/1581
[O]: https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx
[LM]: https://lmstudio.ai/docs/developer/openai-compat
[MLX]: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md
[A]: https://support.apple.com/en-ca/121115
[AF]: https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel
[Q25]: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/README.md
[Q25O]: https://ollama.com/library/qwen2.5:1.5b
[Q3]: https://huggingface.co/Qwen/Qwen3-1.7B/blob/main/README.md
[Q3O]: https://ollama.com/library/qwen3:1.7b
[GO]: https://ollama.com/library/gemma3:1b
[GL]: https://ai.google.dev/gemma/terms
[LO]: https://ollama.com/library/llama3.2:3b
[LL]: https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/LICENSE
