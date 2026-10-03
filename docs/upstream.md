---
purpose: Record primary-source evidence for Handy model-support activity.
scope: Releases, catalog changes, inference-library activity, maintainer statements, and measured catalog-entry lag. No recommendation or forecast.
status: Source-checked snapshot; derived metrics use the definitions below.
---

# Handy upstream model-support activity

Snapshot: **2026-10-03 UTC**. GitHub retrieval used `gh api`, `gh pr list`, `gh issue list`, and `gh api graphql`. GitHub HTML fetch was not used. Model-owner release dates also use primary model cards and announcement pages.

Pinned upstream heads:

- Handy: [`8605699d988ef87e7717cee28fff25c0546bb564`](https://github.com/cjpais/Handy/commit/8605699d988ef87e7717cee28fff25c0546bb564).
- transcribe.cpp: [`077110eb00ca6880e13bef4ddebf766b3b76896c`](https://github.com/handy-computer/transcribe.cpp/commit/077110eb00ca6880e13bef4ddebf766b3b76896c).

## Definitions and data path

```text
GitHub published releases -> tagged model registries -> release-to-release set difference
Handy first-parent history -> catalog slugs -> first default-branch catalog entry
model-owner release date ------------------------------------------> calendar-day lag
transcribe.cpp commit API -> UTC committer-date filter -> counts and active-day gaps
current open PRs/issues + maintainer comments -> dated observations
```

- A **catalog entry** means a `slug` in `src-tauri/src/catalog/catalog.json`. Alternate quantized files do not count as separate entries.
- A **legacy entry** means an explicit `ModelInfo` entry in `src-tauri/src/managers/model.rs`.
- A new GGUF catalog entry can represent a model that Handy already supported through a legacy engine. It is not automatically a newly supported model family.
- Release dates use GitHub `published_at`, not tag author time or release `created_at`.
- Catalog-entry dates use the first **default-branch first-parent** snapshot containing the slug. This excludes earlier development-branch commits that entered main through a later merge.
- Lag uses `UTC calendar date of catalog entry − model public release date`. It does not measure runtime-port completion, experimental test-build availability, or first legacy support.
- Open items are requests or proposed implementations. Their presence does not establish a supported or accepted architecture.

## 1. Releases since v0.8.0

Release dates come from the [GitHub release API][releases]. New entries were computed from tagged registries against the preceding published release. The baseline for v0.8.0 is v0.7.12. Catalog history starts with the transcribe.cpp integration.

| Release | Published UTC | New registry/catalog entries | Tag commit SHA |
|---|---|---|---|
| [v0.8.0](https://github.com/cjpais/Handy/releases/tag/v0.8.0) | 2026-03-23 06:11:40 | None relative to v0.7.12; no catalog.json yet. | `ad75807a6978c9a71389cfd602b7d39c96cf3094` |
| [v0.8.1](https://github.com/cjpais/Handy/releases/tag/v0.8.1) | 2026-03-26 05:50:03 | None; no catalog.json yet. | `233db14d7251384d3088b51fb6b6905ba26158e4` |
| [v0.8.2](https://github.com/cjpais/Handy/releases/tag/v0.8.2) | 2026-04-02 00:53:36 | Legacy `cohere-int8` (Cohere Transcribe). | `39e855deb8da7577a8f44b79d27e67697771816e` |
| [v0.8.3](https://github.com/cjpais/Handy/releases/tag/v0.8.3) | 2026-04-28 00:20:07 | None; no catalog.json yet. | `085cd530a30db479822125c758613c38fe0771b0` |
| [v0.9.0](https://github.com/cjpais/Handy/releases/tag/v0.9.0) | 2026-07-01 14:01:57 | First GGUF catalog: **65 entries**, listed below. Includes existing models and new ones. | `9b0d8a1120810dac1b139f480d37ba5f704e4856` |
| [v0.9.1](https://github.com/cjpais/Handy/releases/tag/v0.9.1) | 2026-07-10 13:11:06 | No new slugs; 65 catalog entries. | `1c4f21acd2bab81f75a0cd7556cd3bb7399ffd9a` |
| [v0.9.2](https://github.com/cjpais/Handy/releases/tag/v0.9.2) | 2026-07-12 12:56:33 | No new slugs; 65 entries. | `ea10f7454e86f893581f5a380a15866476aa6423` |
| [v0.9.3](https://github.com/cjpais/Handy/releases/tag/v0.9.3) | 2026-07-15 13:43:59 | No new slugs; 65 entries. | `b9925d01972a933544d0344a2e62360580368f18` |
| [v0.9.4](https://github.com/cjpais/Handy/releases/tag/v0.9.4) | 2026-07-21 08:13:47 | No new slugs; 65 entries. The same-day catalog additions below occurred after this release. | `17d6c763413e3e29ec5cee76aa19ad01eccb73b2` |
| [v0.9.5](https://github.com/cjpais/Handy/releases/tag/v0.9.5) | 2026-08-08 01:29:48 | `cohere-transcribe-arabic-07-2026`, `multitalker-parakeet-streaming-0.6b-v1`; 67 entries. | `db003f38b1aef4eb967ac3419bebc851d680f71c` |
| [v0.9.6](https://github.com/cjpais/Handy/releases/tag/v0.9.6) | 2026-08-24 08:55:57 | `moss-transcribe-diarize`, `parakeet-primeline`; 69 entries. | `af48dd68a64d58aad128fdbb920492a03da53c79` |
| [v0.9.7](https://github.com/cjpais/Handy/releases/tag/v0.9.7) | 2026-09-18 14:11:52 | No new slugs; 69 entries. Runtime dependency updated to transcribe-cpp 0.2.3 in release notes. | `05e0aedd2906f0d82722735f930465950c476b90` |
| [v0.9.8](https://github.com/cjpais/Handy/releases/tag/v0.9.8) | 2026-10-03 02:42:15 | No new slugs; 69 entries. Runtime dependency updated to transcribe-cpp 0.2.4 in release notes. | `14f6f0d31cb22a4268acfbddba3052820fd0a06e` |

Registry sources: [v0.8.2 legacy table][legacy082], [v0.9.0 catalog][catalog090], [v0.9.5 catalog][catalog095], [v0.9.6 catalog][catalog096], [v0.9.8 catalog][catalog098]. Every tag SHA above can replace the tag in a source URL to pin the same file.

### First catalog: complete slug list

These are the 65 entries in [v0.9.0][catalog090]. Capitalization follows the file. This list records the GGUF catalog migration; Whisper, Parakeet, Cohere, and other legacy models did not all debut as model support in this release.

```text
Breeze-ASR-25
Fun-ASR-MLT-Nano-2512
Fun-ASR-Nano-2512
Qwen3-ASR-0.6B
Qwen3-ASR-1.7B
SenseVoiceSmall
Voxtral-Mini-3B-2507
Voxtral-Mini-4B-Realtime-2602
Voxtral-Small-24B-2507
canary-180m-flash
canary-1b
canary-1b-flash
canary-1b-v2
canary-qwen-2.5b
cohere-transcribe-03-2026
gigaam-v3-ctc
gigaam-v3-e2e-ctc
gigaam-v3-e2e-rnnt
gigaam-v3-rnnt
granite-4.0-1b-speech
granite-speech-4.1-2b
granite-speech-4.1-2b-nar
granite-speech-4.1-2b-plus
medasr
moonshine-base
moonshine-base-ar
moonshine-base-ja
moonshine-base-ko
moonshine-base-uk
moonshine-base-vi
moonshine-base-zh
moonshine-streaming-medium
moonshine-streaming-small
moonshine-streaming-tiny
moonshine-tiny
moonshine-tiny-ar
moonshine-tiny-ja
moonshine-tiny-ko
moonshine-tiny-uk
moonshine-tiny-vi
moonshine-tiny-zh
nemotron-3.5-asr-streaming-0.6b
nemotron-speech-streaming-en-0.6b
parakeet-ctc-0.6b
parakeet-ctc-1.1b
parakeet-rnnt-0.6b
parakeet-rnnt-1.1b
parakeet-tdt-0.6b-v2
parakeet-tdt-0.6b-v3
parakeet-tdt-1.1b
parakeet-tdt_ctc-1.1b
parakeet-tdt_ctc-110m
parakeet-unified-en-0.6b
whisper-base
whisper-base.en
whisper-large
whisper-large-v2
whisper-large-v3
whisper-large-v3-turbo
whisper-medium
whisper-medium.en
whisper-small
whisper-small.en
whisper-tiny
whisper-tiny.en
```

### Catalog changes between releases

| Default-branch event, UTC | Change | Source commit |
|---|---|---|
| 2026-07-01 12:38:20 | Catalog introduced with transcribe.cpp integration. | [`31d8fc2442c2412d6e9de6e018cf70edfbc37ca5`](https://github.com/cjpais/Handy/commit/31d8fc2442c2412d6e9de6e018cf70edfbc37ca5) |
| 2026-07-21 12:32:23 | Adds Arabic Cohere, Multitalker Parakeet, and MOSS diarization slugs. | [`e8c73ba700378c7275b9bbf951f3be2e1257c309`](https://github.com/cjpais/Handy/commit/e8c73ba700378c7275b9bbf951f3be2e1257c309) |
| 2026-07-28 07:33:46 | Removes MOSS from the catalog. This explains its absence in v0.9.5 despite an earlier main entry. | [`292db6470e7463487aabb7aad83f18c5831b574c`](https://github.com/cjpais/Handy/commit/292db6470e7463487aabb7aad83f18c5831b574c) |
| 2026-08-19 06:52:43 | Main first-parent merge snapshot restores MOSS and adds Parakeet Primeline. | [`0e5036721ef6f26c3b89ab31bc10cd2ffd6096fb`](https://github.com/cjpais/Handy/commit/0e5036721ef6f26c3b89ab31bc10cd2ffd6096fb) |

The last merge incorporates catalog work from [`afbf44cd5f828bd48ca49588c0cf25dc6d0fc451`](https://github.com/cjpais/Handy/commit/afbf44cd5f828bd48ca49588c0cf25dc6d0fc451), dated 2026-08-19 06:16:35 UTC. First-parent and development-commit dates are distinct measurements.

## 2. transcribe.cpp activity

### Commit cadence over the last complete 90 days

Window: **[2026-07-05 00:00:00, 2026-10-03 00:00:00) UTC**. This excludes the current partial day. Count all commits reachable from the pinned main head returned by the [commit API query][cadence], including merged development commits. Filter by `commit.committer.date`, not author date. This is not a count of PRs, releases, or architecture ports.

| Metric | Derived value |
|---|---:|
| Commits in the window | 56 |
| Active UTC dates | 29 |
| Mean commits per calendar day | 0.6222 |
| Mean commits per week | 4.3556 |
| Median gap between consecutive active dates | 2 days |
| Longest gap between consecutive active dates | 10 days |
| July 5–31 commits | 12 |
| August commits | 25 |
| September commits | 19 |
| October 1–2 commits | 0 |

All metrics derive from [cadence]. Checks: monthly counts sum to 56; mean/week is `56 × 7 / 90`; active-date gaps use the 29 distinct UTC dates. First counted commit: [`666e2bb466591bcac01ab8124cefa7a0f1137382`](https://github.com/handy-computer/transcribe.cpp/commit/666e2bb466591bcac01ab8124cefa7a0f1137382), 2026-07-08. Last: [`e85b30edac87533168863283c1e595bf39bd7d15`](https://github.com/handy-computer/transcribe.cpp/commit/e85b30edac87533168863283c1e595bf39bd7d15), 2026-09-30.

Examples of model work inside the window:

| Date UTC | Observed commit | SHA |
|---|---|---|
| 2026-07-13 | Parakeet Multitalker | [`fd8b8f8197c9`](https://github.com/handy-computer/transcribe.cpp/commit/fd8b8f8197c9) |
| 2026-07-13 | MOSS Transcribe Diarize | [`5a5a49664a8e`](https://github.com/handy-computer/transcribe.cpp/commit/5a5a49664a8e) |
| 2026-07-28 | Sortformer diarization | [`c87109304c42`](https://github.com/handy-computer/transcribe.cpp/commit/c87109304c42) |
| 2026-08-17 | Parakeet Primeline | [`57ddbe16023e`](https://github.com/handy-computer/transcribe.cpp/commit/57ddbe16023e) |
| 2026-09-12 | Granite 5.0 | [`585b98f7e667`](https://github.com/handy-computer/transcribe.cpp/commit/585b98f7e667) |

These are commit subjects, not independent runtime acceptance tests.

### Supported model families

The [pinned README][cpp-readme] lists the following ASR families or family groups:

1. Canary
2. Canary-Qwen
3. Cohere Transcribe
4. Fun-ASR-Nano
5. GigaAM-v3
6. Granite Speech 4 / 4.1
7. Granite Speech 5.0 TurboCTC
8. MedASR
9. Moonshine
10. Moonshine Streaming
11. MOSS-Transcribe-Diarize
12. Multitalker Parakeet Streaming
13. Nemotron 3.5 ASR Streaming
14. Nemotron Speech Streaming EN
15. Parakeet
16. Qwen3-ASR
17. SenseVoice Small
18. Voxtral offline
19. Voxtral Realtime
20. Whisper, including Breeze

The same README lists Streaming Sortformer Diarizer as a separate **diarization-only** family. Its introductory text says “16 model families,” while the generated ASR table has 20 rows. This report uses the table contents and preserves the discrepancy. Documentation support does not establish successful inference on every backend or that every runtime model is in Handy's release catalog.

### Open architecture/model requests and implementations

Snapshot counts: **13 open PRs** and **22 open issues**, retrieved separately to avoid treating PRs as issues. Sources: [open PR API][openprs] and [open issue API][openissues]. The REST issues endpoint also returns PR records; exclude records with a `pull_request` field when reproducing the issue count. The items below are the model/architecture subset; the other open items concern backends, memory, packaging, timestamps, prompting, and bugs.

| Open item | Type | Scope established by its title/body |
|---|---|---|
| [PR #175](https://github.com/handy-computer/transcribe.cpp/pull/175) | Proposed port | Nemotron 3 diarization; paired request [issue #170](https://github.com/handy-computer/transcribe.cpp/issues/170). Body is empty; readiness is not established. |
| [PR #52](https://github.com/handy-computer/transcribe.cpp/pull/52) | Proposed port | VibeVoice ASR; paired request [issue #109](https://github.com/handy-computer/transcribe.cpp/issues/109). Body is empty; readiness is not established. |
| [PR #104](https://github.com/handy-computer/transcribe.cpp/pull/104) | New variant | Persian FastConformer Hybrid Large through the existing Parakeet conversion family. This is not a new architecture family. |
| [Issue #105](https://github.com/handy-computer/transcribe.cpp/issues/105) | New family request | Meta omnilingual-asr. |
| [Issue #91](https://github.com/handy-computer/transcribe.cpp/issues/91) | New family request | wav2vec2, including converter, C++ architecture, reference checks, and quantization evaluation. |
| [Issue #87](https://github.com/handy-computer/transcribe.cpp/issues/87) | New model requests | GigaAM-Multilingual and GigaChat3.1-Audio. |
| [Issue #125](https://github.com/handy-computer/transcribe.cpp/issues/125) | Model request | Crisper Whisper 2.0. |
| [Issue #152](https://github.com/handy-computer/transcribe.cpp/issues/152) | Variant request | NB-Whisper Norwegian fine-tunes in the existing Whisper family. |

No merge or support date is inferred from these open items.

## 3. The replacement library mentioned in PR #1435

On **2026-05-27**, cjpais wrote: “custom transcription endpoints will not be added” and “I am working on a library to replace the existing onnx and whisper inference engines and it will support MedASR day 1 when it is merged into Handy.” Exact source: [maintainer comment on #1435][1435-comment].

Observed state:

- [PR #1435][1435] is **closed and unmerged**. Its proposal was a custom local transcription endpoint. The PR's `merged_at` is null; a non-null API `merge_commit_sha` alone must not be treated as a merge receipt.
- The named integration arrived as [PR #1529][1529], “introduce transcribe.cpp.” It merged on **2026-07-01 12:38:20 UTC**, commit [`31d8fc2442c2412d6e9de6e018cf70edfbc37ca5`](https://github.com/cjpais/Handy/commit/31d8fc2442c2412d6e9de6e018cf70edfbc37ca5).
- Its body calls transcribe.cpp the primary transcription engine. The [v0.9.0 release](https://github.com/cjpais/Handy/releases/tag/v0.9.0) explicitly attributes streaming support and new models to this integration.
- The resulting [initial catalog][catalog090] includes `medasr`. The [library README][cpp-readme] lists MedASR. These establish release/catalog support, not a test on this Mac.
- The library uses GGUF/ggml with CPU, Metal, Vulkan, and CUDA paths. It has Python, Rust, and TypeScript bindings in the [README][cpp-readme].
- The migration did **not** immediately remove legacy ONNX. The maintainer said the ONNX models would be deprecated later and kept cross-compatibility during the transition: [comment on #1529][1529-legacy]. Handy's [v0.9.8 Cargo.toml][cargo098] still declares `transcribe-rs` with ONNX alongside `transcribe-cpp`.

**Provisional identification:** #1435 did not name the library. The later integration, maintainer explanations, and MedASR catalog entry identify transcribe.cpp as the replacement work. This is a source-supported connection between two events, not a direct name in the earlier comment.

## 4. Maintainer statements and contribution policy

| Date / source | Observation |
|---|---|
| [v0.8.0 release, 2026-03-23](https://github.com/cjpais/Handy/releases/tag/v0.8.0) | Lists future streaming, Handy as an ASR API server, local-file transcription, and eventual local post-processing with a fine-tuned model. These are roadmap statements, not proof each item shipped. |
| [#1435 comment, 2026-05-27][1435-comment] | Rejects custom transcription endpoints and favors direct model support through the replacement library. |
| [#1529 maintainer comment][1529-porting] | Describes porting existing models to ggml and seeking a unified GPU/distribution path. It was a development-stage statement. |
| [#1581 maintainer comment, 2026-07-02][1581-comment] | Directs users to `handy-computer` conversions and says only models converted through transcribe.cpp are supported. Existing arbitrary GGUF files may use incompatible one-off engines. Also states an eventual local-only direction for LLM cleanup. |
| [#1688 comment, 2026-07-15][1688-comment] | For new GigaAM requests: “Please add an issue to handy-computer/transcribe.cpp.” The linked request became [library issue #87](https://github.com/handy-computer/transcribe.cpp/issues/87). |
| [#847 comment, 2026-08-30][847-comment] | Says bundled local LLM integration is a longer-term packaging project; application stability currently has priority. |
| [Pinned CONTRIBUTING.md][contributing] and [PR template][template] | Feature freeze remains stated. Unrequested new features are rejected; demonstrated community demand may allow consideration. Bug fixes and stability take priority. Feature requests belong in Discussions. |

The policy documents contain a “60+ issues” sentence. That is policy text, not this report's current live issue count. The listed statements have different dates and scopes. This report does not turn them into a promised delivery schedule.

## 5. Public-release-to-catalog lag

Five examples were selected from the requested model families and Voxtral Realtime. Public release dates come from model owners. Both Qwen sizes share one family release date and therefore count as **one example**, not two independent samples.

All five slugs first enter the default-branch catalog at [`31d8fc2442c2412d6e9de6e018cf70edfbc37ca5`](https://github.com/cjpais/Handy/commit/31d8fc2442c2412d6e9de6e018cf70edfbc37ca5), **2026-07-01**. Their earlier development-branch snapshots do not change that main-entry definition.

| Model | Owner public release date | First catalog entry UTC | Derived calendar-day lag | Date source |
|---|---|---|---:|---|
| Parakeet TDT v3 | 2025-08-14 | 2026-07-01 | 321 | [NVIDIA card][parakeet-release] explicitly lists Hugging Face release date. |
| Qwen3-ASR family | 2026-01-29 | 2026-07-01 | 153 | [Qwen repository News][qwen-release] states the series was released that day. |
| Granite Speech 4.1 2B | 2026-04-29 | 2026-07-01 | 63 | [IBM model card][granite-release] explicitly lists Release Date. |
| Cohere Transcribe | 2026-03-26 | 2026-07-01 | 97 | [Cohere release announcement][cohere-release], `datePublished` and visible publication date. |
| Voxtral Mini Realtime | 2026-02-04 | 2026-07-01 | 147 | [Mistral release announcement][voxtral-release], `datePublished` and visible publication date. |

**Derived median: 147 calendar days.** Sorted lags: `[63, 97, 147, 153, 321]`; the middle value is 147. This describes this small catalog-migration sample only.

### Earlier legacy support is a different metric

- Parakeet v3 entered the legacy table at [`45a473dc9fa8fe3ae67fc5314039eaf81f478643`](https://github.com/cjpais/Handy/commit/45a473dc9fa8fe3ae67fc5314039eaf81f478643), **2025-09-10 UTC**. Its commit displays September 9 in a UTC−07 offset. Calendar lag from the owner's release date is **27 days**.
- Cohere entered the legacy table at [`4609db7fdbe6c90c69cb8b171e3007b10066f927`](https://github.com/cjpais/Handy/commit/4609db7fdbe6c90c69cb8b171e3007b10066f927), **2026-04-01 UTC**, **6 days** after its public release. It first shipped in v0.8.2.

These two values must not be mixed with the JSON-catalog lags above. No median for a five-model historical-native-support sample is claimed. Experimental builds, announcement dates, repository creation dates, and private pre-release commits are also different measurements.

## Reproduction and verification

No app, model, or user settings were changed. Existing local Git objects supplied historical tagged files; current GitHub state came through `gh`.

```bash
# Published dates and release bodies.
gh api repos/cjpais/Handy/releases --paginate

# Tagged JSON; decode .content before comparing sets of .models[].slug.
gh api 'repos/cjpais/Handy/contents/src-tauri/src/catalog/catalog.json?ref=v0.9.8'

# First default-branch appearance; inspect each snapshot, not just commit subjects.
git -C handy log --first-parent --reverse --format='%H %cI' v0.9.7 -- src-tauri/src/catalog/catalog.json

# Cadence input is pinned; manually filter committer timestamps to the half-open window.
gh api 'repos/handy-computer/transcribe.cpp/commits?sha=077110eb00ca6880e13bef4ddebf766b3b76896c&since=2026-07-05T00:00:00Z&until=2026-10-03T00:00:00Z&per_page=100' --paginate

gh pr list -R handy-computer/transcribe.cpp --state open --limit 500
gh issue list -R handy-computer/transcribe.cpp --state open --limit 500
```

Checks performed:

- Tag-by-tag catalog and legacy-entry differences, including removal and restoration of MOSS.
- Current v0.9.8 catalog retrieved independently through `gh`; it has the same slug set as v0.9.7.
- Pinned and initial cadence requests return the same commit SHA list. All counted committer timestamps fit the stated window.
- PR state uses `merged`/`merged_at`; it does not infer a merge from an API comparison SHA.
- Public-date passages were checked in the owner cards/announcements; the median was recomputed from the five displayed rows.

### Source URLs

[releases]: https://api.github.com/repos/cjpais/Handy/releases?per_page=100
[legacy082]: https://github.com/cjpais/Handy/blob/39e855deb8da7577a8f44b79d27e67697771816e/src-tauri/src/managers/model.rs
[catalog090]: https://github.com/cjpais/Handy/blob/9b0d8a1120810dac1b139f480d37ba5f704e4856/src-tauri/src/catalog/catalog.json
[catalog095]: https://github.com/cjpais/Handy/blob/db003f38b1aef4eb967ac3419bebc851d680f71c/src-tauri/src/catalog/catalog.json
[catalog096]: https://github.com/cjpais/Handy/blob/af48dd68a64d58aad128fdbb920492a03da53c79/src-tauri/src/catalog/catalog.json
[catalog098]: https://github.com/cjpais/Handy/blob/14f6f0d31cb22a4268acfbddba3052820fd0a06e/src-tauri/src/catalog/catalog.json
[cargo098]: https://github.com/cjpais/Handy/blob/14f6f0d31cb22a4268acfbddba3052820fd0a06e/src-tauri/Cargo.toml
[cadence]: https://api.github.com/repos/handy-computer/transcribe.cpp/commits?sha=077110eb00ca6880e13bef4ddebf766b3b76896c&since=2026-07-05T00:00:00Z&until=2026-10-03T00:00:00Z&per_page=100
[cpp-readme]: https://github.com/handy-computer/transcribe.cpp/blob/077110eb00ca6880e13bef4ddebf766b3b76896c/README.md
[openprs]: https://api.github.com/repos/handy-computer/transcribe.cpp/pulls?state=open&per_page=100
[openissues]: https://api.github.com/repos/handy-computer/transcribe.cpp/issues?state=open&per_page=100
[1435]: https://github.com/cjpais/Handy/pull/1435
[1435-comment]: https://github.com/cjpais/Handy/pull/1435#issuecomment-4550589140
[1529]: https://github.com/cjpais/Handy/pull/1529
[1529-porting]: https://github.com/cjpais/Handy/pull/1529#issuecomment-4760325798
[1529-legacy]: https://github.com/cjpais/Handy/pull/1529#issuecomment-4768045136
[1581-comment]: https://github.com/cjpais/Handy/discussions/1581#discussioncomment-17510928
[1688-comment]: https://github.com/cjpais/Handy/discussions/1688#discussioncomment-17648984
[847-comment]: https://github.com/cjpais/Handy/discussions/847#discussioncomment-18202522
[contributing]: https://github.com/cjpais/Handy/blob/8605699d988ef87e7717cee28fff25c0546bb564/CONTRIBUTING.md
[template]: https://github.com/cjpais/Handy/blob/8605699d988ef87e7717cee28fff25c0546bb564/.github/PULL_REQUEST_TEMPLATE.md
[parakeet-release]: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/blob/main/README.md
[qwen-release]: https://github.com/QwenLM/Qwen3-ASR/blob/7c6daf77a2421100f5fb066495372c00129d39ff/README.md#news
[granite-release]: https://huggingface.co/ibm-granite/granite-speech-4.1-2b/blob/de575db64086f84fdc79da4932d1076e965bc546/README.md
[cohere-release]: https://huggingface.co/blog/CohereLabs/cohere-transcribe-03-2026-release
[voxtral-release]: https://mistral.ai/news/voxtral-transcribe-2/
