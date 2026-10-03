---
purpose: Locate open-weight English ASR candidates for local Handy dictation.
scope: Published accuracy, weight sizes, licenses, runtime paths, and tagged Handy support. Local benchmarks belong in server/results.md.
status: Exploration survey; runtime compatibility is source-checked, not locally tested.
---

# English open-weight ASR survey

Checked on 2026-10-03. This is an October snapshot, not a forecast for the rest of the month.

## Findings

- **No verified candidate meets both priorities:** clearly better English accuracy than Parakeet v3 and a download near or below 700 MB. Quantized downloads have no matching leaderboard evaluation in the sources checked.
- **Qwen3-ASR-1.7B is the best open-weight row in the checked English short-form leaderboard:** mean WER **4.31125%**, versus Parakeet v3 **4.85875%** [L]. Its smallest Handy catalog GGUF is **1,319.8 MB** [H]. MLX is available [M]. Its quantized accuracy and local memory fit remain provisional.
- **Phonon-2 is exceptionally compact, but does not beat Parakeet v3 overall.** The current leaderboard reports **5.16875%** versus **4.85875%** [L]. Fermion reports **164 MB** download and **178 MB** installed [P2]. Its publisher's “most accurate under 900 MB” claim does not establish an upgrade over a quantized Parakeet baseline [P].
- **The user's Parakeet size estimate matches a GGUF variant.** Handy's default v3 Q8 file is **739.5 MB**; Q6 is **610.3 MB** [H]. The unquantized MLX checkpoint is **2,508.3 MB** [S-P]. Model identity alone does not specify disk size or accuracy.
- **Handy already catalogs many requested models.** The tagged catalog includes Unified, Canary-Qwen, Cohere, Granite, Qwen3-ASR, and Voxtral [H]. A cloud-provider patch is not required merely to access those model families. Local serving still enables a shared endpoint and Fermion's custom format.
- **MAI-Transcribe is excluded from offline candidates.** Microsoft documents hosted API access. No downloadable weights or open-weight license were located [MAI]. This is a bounded search result, not proof that Microsoft can never release weights.

## Evidence method

```text
HF English short-form CSV -> exact model rows -> comparable mean and per-set WER
model cards + HF file metadata -> licenses + actual artifact sizes
Handy tagged catalog + loader source -> built-in model availability
runtime docs + server source -> documented macOS serving paths
                              -> local tests still required
```

[L] is a pinned leaderboard CSV. All WER and RTFx pairs in the main table come from that same snapshot unless the cell says otherwise. Lower WER is better. Higher RTFx is faster. RTFx measures benchmark throughput; it is not warm dictation latency on this Mac. The current average uses the cleaned benchmark columns plus Voice Arena. Old cards can use different datasets, normalization, and decoding settings.

Sizes use decimal MB and GB. Catalog sizes are exact file byte counts rounded for display. They exclude tokenizers, caches, Python packages, and working memory. A quantization label does not guarantee that every tensor has that precision. Parameter labels can refer to the decoder rather than the complete ASR network.

“Native” means the tagged Handy catalog offers the model or its legacy loader offers it. It does not mean this survey ran the installed app. **All server/model combinations below are source-backed candidates; none has an endpoint smoke test here.** “Not located” records a search limit, not an incompatibility claim.

## Candidate table

[H] supplies GGUF parameter labels, sizes, native support, and its runtime streaming flags. [M] supplies MLX runtime and HTTP support. [T] supplies transcribe.cpp family support. License links in model names point to the original weight owner.

| Model / original weights | Params | Download / quantized weight sizes | Open weights + license | Mean English WER % / RTFx [L] | Streaming audio | Apple Silicon runtime | Existing OpenAI-compatible server on macOS | Native Handy [H, HM] |
|---|---|---|---|---|---|---|---|---|
| [Parakeet TDT v3][PV3] | 0.6B [H] | GGUF F16 1,255.9 MB; Q8 739.5 MB; Q6 610.3 MB; Q4 485.4 MB [H]. MLX F32 2,508.3 MB [S-P] | Yes; CC-BY-4.0 [PV3] | 4.85875 / 6,076.07 | No in catalog; buffered partial transcription is a separate runtime feature [H] | MLX/parakeet-mlx [M, PM]; GGUF/Metal [T]; legacy ONNX [HM] | mlx-audio [M] | Yes, GGUF + legacy ONNX |
| [Parakeet Unified EN][U] | 0.6B [H] | NeMo 2,474.1 MB [S-U]; GGUF F16 1,239.1 MB; Q8 731.4 MB; Q6 602.2 MB; Q4 477.3 MB [H] | Yes; NVIDIA Open Model License [U]. Catalog metadata says CC-BY; use original terms | Not present in [L]. Card: offline 5.91%; streaming 6.29% at 1.12 s [U]; not comparable to [L] | Yes; buffered RNNT, minimum 160 ms in card [U] | GGUF/Metal in Handy [H]; NeMo reference [U]. MLX implementation not located | No macOS OpenAI server verified for this exact variant; native Handy is a direct path | Yes |
| [Phonon-2][P] | 0.6B [L] | 164 MB download; 178 MB installed; low-bit encoder about 2.1 bits/weight [P, P2] | Yes; CC-BY-4.0 weights; Apache-2.0 runtime [P] | 5.16875 / 1,972.71 | Live buffered hypotheses and WebSocket API; does not establish a causal encoder [PS] | Fermion's MLX engine on macOS [P, PS] | `fermion serve phonon-2` / `phonon serve` [PS] | No catalog entry; custom transport is not ordinary GGUF |
| [Microsoft MAI-Transcribe][MAI] | Not disclosed in checked source | No weight artifact located | No open-weight release located; hosted API [MAI] | No exact MAI row in [L]; Azure Speech rows are not a safe substitute | Hosted streaming variant exists [MAI2] | No offline runtime located | Remote API only located; fails offline requirement | No |
| [Granite Speech 4.1 2B][G] | 2B product name; 2.3B catalog total [G, H] | GGUF BF16 4,631.6 MB; Q5 1,829.7 MB; Q4 1,602.9 MB [H] | Yes; Apache-2.0 [G] | 4.615 / 545.64 | No catalog audio streaming. Incremental generated text does not imply streaming input [H, GM] | MLX [G, GM]; GGUF/Metal [T] | mlx-audio [M, GM] | Yes |
| [Granite Speech 4.1 2B NAR][GN] | 2.3B [H] | GGUF BF16 4,514.7 MB; Q5 1,782.1 MB; Q4 1,560.0 MB [H] | Yes; Apache-2.0 [GN] | 4.675 / 2,073.53 | No [H] | MLX [GM]; GGUF/Metal [T] | mlx-audio [M, GM]; NAR conversion must load successfully | Yes |
| [Cohere Transcribe][C] | 2B [C, L] | GGUF BF16 4,105.3 MB; Q5 1,770.3 MB; Q4 1,558.2 MB [H]. Community MLX “int8” file 4,131.8 MB [S-C] | Yes; Apache-2.0 [C] | 4.67 / 906.56 | No [H] | GGUF/Metal [T]; ONNX legacy [HM]; separate community MLX port [CM] | No mature OpenAI macOS server verified for the separate MLX port. Do not assume generic mlx-audio loads it | Yes, GGUF + legacy ONNX |
| [Canary-Qwen][CQ] | 2.5B [CQ] | HF safetensors 5,119.1 MB [S-CQ]; GGUF BF16 5,076.1 MB; Q5 1,983.7 MB; Q4 1,737.6 MB [H] | Yes; CC-BY-4.0 [CQ] | 4.4275 / 867.09 | No [H] | GGUF/Metal [T]; experimental community MLX port [CQM] | No mature macOS OpenAI server verified. mlx-audio's Canary entry covers Canary ASR, not this SpeechLM [MC] | Yes |
| [Whisper large-v3-turbo][W] | 809M [H] | GGUF F16 1,625.9 MB; Q8 886.4 MB; Q6 692.5 MB; Q4 536.1 MB [H]; MLX FP16 1,614.0 MB [S-W] | Yes; MIT [W] | 6.3575 / 797.03 | No native streaming encoder; chunked applications exist [H, WC] | MLX [M]; whisper.cpp/Metal/CoreML encoder [WC]; transcribe.cpp [T] | mlx-audio [M]; whisper.cpp server uses `/inference`, so endpoint adaptation is required [WS] | Yes |
| [Qwen3-ASR 0.6B][Q] | 0.6B label; HF source total 0.938B [Q, S-Q0] | GGUF Q4 589.6 MB; Q6 690.4 MB; F16 1,579.8 MB [H]; MLX Q4 708.2 MB [S-Q04] | Yes; Apache-2.0 [Q] | 5.045 / 743.96 | Model supports streaming in reference vLLM; Handy GGUF path does not [Q, H] | MLX [M]; GGUF/Metal [T] | mlx-audio [M]. Official vLLM server is not evidence of macOS support | Yes |
| [Qwen3-ASR 1.7B][QB] | 1.7B label; HF source total 2.349B [QB, S-Q1] | GGUF Q4 1,319.8 MB; Q5 1,517.3 MB; F16 4,091.4 MB [H]; MLX Q4 1,603.1 MB [S-Q14] | Yes; Apache-2.0 [QB] | **4.31125 / 819.96** | Reference streaming; GGUF offline [QB, H] | MLX [M]; GGUF/Metal [T] | mlx-audio [M] | Yes |
| [Voxtral Mini Realtime][V] | 4B product name [V] | GGUF BF16 8,868.3 MB; Q4 2,830.5 MB [H]; MLX Q4 3,133.8 MB [S-V] | Yes; Apache-2.0 [V] | 6.4625 / 102.62 | Native streaming; configurable delay 240 ms–2.4 s [V] | MLX [M]; GGUF/Metal [T] | mlx-audio file endpoint and realtime API [MS] | Yes |
| [Voxtral Mini / Small offline][VO] | Mini marketed 3B, leaderboard total 5B; Small 24B [VO, L] | Mini GGUF Q4 2,984.7 MB; BF16 9,365.8 MB. Small Q4 14,302.3 MB; BF16 48,537.3 MB [H] | Yes; Apache-2.0 [VO, L] | Mini 5.53875 / 180.93; Small 4.99375 / 101.26 | No [H] | MLX Mini [M]; GGUF/Metal [T] | mlx-audio Mini [M]; Small loader path needs verification | Yes, both |
| [Hojo-ASR-V1][HO] | 5.18B [L] | HF merged safetensors 11,956.9 MB [S-HO]; no quantized macOS artifact verified | Yes; Apache-2.0 [HO] | 4.33375 / 72.51 | Not established | Custom PyTorch/FunASR runner [HO]; no native macOS accelerated path verified | None verified | No |
| [Higgs Audio v3 STT][HI] | 2.68B [HI] | HF safetensor shards total 5,351.2 MB [S-HI]; no quantized macOS artifact verified | Yes; Apache-2.0 [L, HI] | 4.3925 / 111.23 | Not established | Custom Transformers runner [HI]; MPS support remains provisional | None verified | No |
| [ARK-ASR-3B][ARK] | 3.75B leaderboard label; HF metadata total 4.063B [L, S-ARK] | HF shards 8,127.0 MB [S-ARK]; no quantized macOS artifact verified | Yes; Apache-2.0 [L, ARK] | 4.475 / 481.49 | Not established | Transformers custom model [ARK]; MPS path unverified | None verified | No |
| [TheWhisper Turbo][TW] | 0.8B [L] | HF model 3,235.6 MB [S-TW]; CoreML/ONNX variants exist, but full bundle size not calculated | Yes; CC-BY-4.0 [L, TW] | 4.53875 / 1,180.62 | Not established | Publisher CoreML/ONNX artifacts [S-TW]; not interchangeable with original Whisper without validation | None verified | No exact catalog entry |

## Comparable per-set English WER

All values in this section come from [L]. Columns follow its exact cleaned-set definition. This table must not be combined with older card averages.

| Model | AMI cleaned | Earnings cleaned | GigaSpeech cleaned | LS clean | LS other | SPGI | Voice Arena | VoxPopuli cleaned |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Parakeet v3 | 9.42 | 5.85 | 7.99 | 1.52 | 3.13 | 3.63 | 4.14 | 3.19 |
| Parakeet v2 | 9.09 | 6.76 | 8.15 | 1.28 | 2.73 | 1.94 | 3.89 | 3.78 |
| Phonon-2 | 9.32 | 6.96 | 8.35 | 1.73 | 3.92 | 3.70 | 4.91 | 2.46 |
| Qwen3-ASR small | 9.33 | 7.83 | 7.62 | 1.70 | 4.01 | 2.74 | 4.23 | 2.90 |
| Qwen3-ASR large | 8.31 | 5.84 | 7.22 | 1.26 | 2.94 | 2.57 | 3.50 | 2.85 |
| Granite 4.1 | 7.06 | 6.69 | 8.18 | 1.03 | 2.19 | 3.47 | 4.12 | 4.18 |
| Cohere | 7.02 | 7.88 | 7.88 | 0.97 | 2.05 | 2.74 | 3.44 | 5.38 |
| Canary-Qwen | 7.91 | 6.41 | 7.80 | 1.23 | 2.63 | 1.70 | 3.60 | 4.14 |

## Source conflicts and limits

- Fermion's card gives Phonon-2 a seven-set mean of **5.21%** and its teacher **4.96%** [P]. The current leaderboard gives different means [L]. Both support the same narrow finding: Phonon-2 is smaller and worse overall. Its VoxPopuli score is better. The card's meeting improvement claim does not hold in the current cleaned AMI rows [L].
- Cohere's release card gives **5.42%** on an earlier benchmark mix [C]. Granite's card links an earlier leaderboard visualization [G]. Use [L] for cross-model ranking in this report.
- Parakeet Unified's **5.91%** offline result uses the card's evaluation setup and compares against v2 at **6.04%** [U]. It supplies no same-run v3 comparison. The model's streaming value does not establish that it is a better dictation model.
- The leaderboard's Qwen rows use `-hf` repository names [L]. The GGUF and MLX files convert the original Qwen repositories. They have different total tensor sizes [H, S-Q0, S-Q1]. Architecture conversion, exported heads, normalization, and quantization need local validation before transferring leaderboard scores.
- Unified's tagged Handy catalog lists CC-BY, while its original card specifies NVIDIA Open Model License [H, U]. Treat the original license as controlling. Do not copy the catalog's license into redistribution notices.
- A community Cohere MLX repository says “int8,” but its weight file is **4,131.8 MB** [S-C]. Precision names alone do not establish a small download. The Handy GGUF Q4 file is smaller [H].
- The leaderboard also contains newer Granite TurboCTC variants: **0.47B**, **5.0325% / 20,945.78 RTFx** for the Apache release and **4.84375% / 20,610.53 RTFx** for the noncommercial release [L]. The latter is only slightly below v3. It does not establish a clear accuracy upgrade. mlx-audio documents this family [M]. Exact small quantized download size was not checked.
- Proprietary rows rank above the open models. The best checked row is Zoom Scribe v2 Pro at **3.5925%**, but [L] labels it proprietary. It does not satisfy the local-weight requirement.
- Phonon-1 variants also fit small downloads. Fermion reports **285 MB**, **415 MB**, and **581 MB** downloads, with older benchmark means **8.52%**, **7.67%**, and **7.60%**, respectively [P2]. They are not accuracy upgrades.
- No credible per-model CoreML path was located for Unified, Cohere, Granite, Canary-Qwen, or Qwen3-ASR. GGUF/Metal is the shared native path in Handy [H, HM]. Avoid labeling an arbitrary ONNX export as CoreML-compatible.

## Provisional benchmark shortlist

Local results live in `../server/results.md`. These are candidates, not measured recommendations.

| Role | Candidate | Evidence and unresolved check |
|---|---|---|
| Baseline | Parakeet v3 GGUF Q6 or Q8 | Exact catalog artifact avoids accidentally comparing full-precision MLX with the user's small native variant [H]. Record precision. |
| Compact candidate | Parakeet v2 GGUF Q6 | Q6 is **600.4 MB** [H]. Its original leaderboard mean is **4.7025%**, slightly below v3 [L]. Quantized accuracy is unverified. This is a plausible strict-size candidate, not a clearly better model. |
| Compact alternative | Phonon-2 | Smallest useful compact candidate with an explicit macOS OpenAI API [P2, PS]. Its mean is worse than v3 [L]. Compare only if compactness matters. |
| Accuracy candidate | Qwen3-ASR-1.7B | Best checked open leaderboard mean [L]. mlx-audio offers a shared multi-model endpoint [M, MS]. Compare its MLX Q4/Q8 or native GGUF; do not reuse the unquantized WER as a quantized result. |
| Accuracy fallback | Granite 4.1 or NAR | Both have MLX and native GGUF paths [GM, H]. Their meeting scores are strong [L]. Test if Qwen loses on dictation or has loader issues. |

Qwen's and Granite's weight files suggest that they can fit a 32 GB M4 Mac, but this is **provisional inference**. Disk size excludes activations, caches, temporary allocations, and other apps. Only peak RSS and a sustained local run can establish fit.

### Server boundaries

- **mlx-audio:** Its source implements `POST /v1/audio/transcriptions` with multipart `model` selection [MS]. Its README shows the file route [M]. Use an explicit loopback bind and the contract's port. A documented architecture plus this route establishes a candidate path; it does not establish successful conversion or quantized accuracy.
- **Fermion:** `fermion serve phonon-2` exposes the transcription route, model listing, and live WebSocket route [PS]. The form `model` is checked against the served model. This is a single-model server; it does not by itself satisfy simultaneous Parakeet/Qwen/Phonon routing.
- **whisper.cpp:** Its mature server defaults to `/inference`; `--inference-path` changes the route [WS]. Route naming alone does not prove full OpenAI semantics. Check multipart fields and JSON output before using it in the PoC.
- **transcribe.cpp:** The native library covers the required GGUF families and Metal [T]. A runtime library is not an OpenAI HTTP server. No bundled mature OpenAI endpoint was verified in the checked README.
- **CUDA-focused servers:** Official vLLM examples [Q, V] do not establish support on this Mac. Speaches or a Linux container also needs a working macOS backend before it is a local candidate. No CUDA dependency should enter the default Mac launch path.

## Sources

URLs below are primary model-owner cards, runtime-owner code, or publisher artifact metadata. HF tree pages show individual file sizes. API URLs expose raw byte sizes and safetensor parameter totals. Rounded table sizes derive from those bytes. The pinned leaderboard and tagged Handy catalog define this report's reproducible comparison.

[L]: https://huggingface.co/datasets/hf-audio/open-asr-leaderboard-results/blob/0860bf2a924fd275ecee333545525eac8d5579cb/english_short_latest.csv
[H]: https://github.com/cjpais/Handy/blob/v0.9.7/src-tauri/src/catalog/catalog.json
[HM]: https://github.com/cjpais/Handy/blob/v0.9.7/src-tauri/src/managers/model.rs
[M]: https://github.com/Blaizzy/mlx-audio/blob/main/README.md
[MS]: https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/server.py
[T]: https://github.com/handy-computer/transcribe.cpp/blob/main/README.md
[PM]: https://github.com/senstella/parakeet-mlx
[PV3]: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/blob/main/README.md
[U]: https://huggingface.co/nvidia/parakeet-unified-en-0.6b/blob/fe53cd885760c96b6a5f51a0bfd362cb4584a98b/README.md
[P]: https://huggingface.co/FermionResearch/Phonon-2/blob/ca1bef26bcd8ef4a7e16d0636d8a77bb25e298ee/README.md
[P2]: https://www.fermionresearch.com/docs/speech-models/
[PS]: https://www.fermionresearch.com/docs/speech/
[MAI]: https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-services/speech-service/mai-transcribe.md
[MAI2]: https://microsoft.ai/news/our-first-streaming-transcription-model/
[G]: https://huggingface.co/ibm-granite/granite-speech-4.1-2b/blob/de575db64086f84fdc79da4932d1076e965bc546/README.md
[GN]: https://huggingface.co/ibm-granite/granite-speech-4.1-2b-nar
[GM]: https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/stt/models/granite_speech/README.md
[C]: https://huggingface.co/CohereLabs/cohere-transcribe-03-2026/blob/main/README.md
[CM]: https://huggingface.co/mlx-community/cohere-transcribe-03-2026-mlx-8bit/blob/main/README.md
[CQ]: https://huggingface.co/nvidia/canary-qwen-2.5b/blob/b1469e1bba1cfe140205529c79c434ca47180960/README.md
[CQM]: https://huggingface.co/speechllms/canary-speechlm-mlx
[MC]: https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/stt/models/canary/README.md
[W]: https://huggingface.co/openai/whisper-large-v3-turbo/blob/main/README.md
[WC]: https://github.com/ggml-org/whisper.cpp/blob/master/README.md
[WS]: https://github.com/ggml-org/whisper.cpp/blob/master/examples/server/README.md
[Q]: https://huggingface.co/Qwen/Qwen3-ASR-0.6B/blob/5eb144179a02acc5e5ba31e748d22b0cf3e303b0/README.md
[QB]: https://huggingface.co/Qwen/Qwen3-ASR-1.7B/blob/7278e1e70fe206f11671096ffdd38061171dd6e5/README.md
[V]: https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602/blob/main/README.md
[VO]: https://huggingface.co/mistralai/Voxtral-Mini-3B-2507/blob/main/README.md
[HO]: https://huggingface.co/HojoAI/Hojo-ASR-V1/blob/a22c381896ce5f4b70038982bfb888fe9969ed99/README.md
[HI]: https://huggingface.co/bosonai/higgs-audio-v3-stt/blob/2ffd1aa39f5a1266931e405cba12e404a9f994b2/README.md
[ARK]: https://huggingface.co/AutoArk-AI/ARK-ASR-3B
[TW]: https://huggingface.co/TheStageAI/thewhisper-large-v3-turbo
[S-P]: https://huggingface.co/mlx-community/parakeet-tdt-0.6b-v3/tree/ed2b7e8c15f9aaa0b5772e2efb986255eaef7e15
[S-U]: https://huggingface.co/nvidia/parakeet-unified-en-0.6b/tree/fe53cd885760c96b6a5f51a0bfd362cb4584a98b
[S-C]: https://huggingface.co/mlx-community/cohere-transcribe-03-2026-mlx-8bit/tree/a0acb7f93cd32d82c4fbf801b6d8fb39d20c509f
[S-CQ]: https://huggingface.co/nvidia/canary-qwen-2.5b/tree/b1469e1bba1cfe140205529c79c434ca47180960
[S-W]: https://huggingface.co/mlx-community/whisper-large-v3-turbo-asr-fp16/tree/624c19c9af5603fa73b83bce14d4aeea96156d18
[S-Q0]: https://huggingface.co/api/models/Qwen/Qwen3-ASR-0.6B/revision/5eb144179a02acc5e5ba31e748d22b0cf3e303b0?blobs=true
[S-Q1]: https://huggingface.co/api/models/Qwen/Qwen3-ASR-1.7B/revision/7278e1e70fe206f11671096ffdd38061171dd6e5?blobs=true
[S-Q04]: https://huggingface.co/mlx-community/Qwen3-ASR-0.6B-4bit/tree/313d850181767edf09f00a9c289becca70e58cd0
[S-Q14]: https://huggingface.co/mlx-community/Qwen3-ASR-1.7B-4bit/tree/78a389c776a5483b2d0d4ea5494e11012e0d6159
[S-V]: https://huggingface.co/mlx-community/Voxtral-Mini-4B-Realtime-2602-4bit/tree/fdebf7b2af834a1db4b8a3c99ab7480b333adf9e
[S-HO]: https://huggingface.co/HojoAI/Hojo-ASR-V1/tree/a22c381896ce5f4b70038982bfb888fe9969ed99
[S-HI]: https://huggingface.co/bosonai/higgs-audio-v3-stt/tree/2ffd1aa39f5a1266931e405cba12e404a9f994b2
[S-ARK]: https://huggingface.co/api/models/AutoArk-AI/ARK-ASR-3B/revision/1e28271b79edc97635783bea65abc89195a09ed3?blobs=true
[S-TW]: https://huggingface.co/TheStageAI/thewhisper-large-v3-turbo/tree/5ce95e7a5890cb2191c5c783d8f818f799930705
