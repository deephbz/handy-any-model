"""Render normalization checks and Qwen error examples from saved scores."""
import json
from pathlib import Path
here = Path(__file__).resolve().parent
j = json.loads((here / 'normalization.json').read_text())
lines = ['# Normalization and Qwen error checks', '', 'Observed scores use the exact pinned Open ASR Leaderboard `EnglishTextNormalizer`.', j['normalizer_source'], '', 'The first benchmark used lowercase text and punctuation removal. It did not expand', 'numbers, contractions, fillers, or compound words. This penalized Qwen formatting.', 'Verbatim WER also preserves reference casing. LibriSpeech and AMI use uppercase', 'references. Verbatim WER is reported for completeness; it is not a useful ranking.', '', '## Per-set scores', '', '| Model | Set | Verbatim WER | Simple WER | Open ASR WER | Open ASR edits / words |', '|---|---|---:|---:|---:|---:|']
for m in j['models']:
    for group, d in m['per_set'].items():
        n = d['leaderboard']
        lines.append(f"| {m['key']} | {group} | {d['verbatim']['wer']:.2%} | {d['simple']['wer']:.2%} | {n['wer']:.2%} | {n['errors']} / {n['words']} |")
lines += ['', '## Error categories', '', 'Counts below flag clips whose edit count decreased after Open ASR normalization.', 'Flags overlap. They use text-pattern heuristics. They do not attribute each edit.', 'Residual edit counts come from exact normalized word alignment.', 'A residual edit can still reflect reference conventions or a reference error.', '', '| Model | Numbers/titles | Hyphens/compounds | Contractions | Abbreviations | Fillers | Residual S / D / I |', '|---|---:|---:|---:|---:|---:|---:|']
for m in j['models']:
    c = m['normalization_sensitive_clip_flags']
    e = m['residual_edits']
    lines.append(f"| {m['key']} | {c['numbers_or_titles']} | {c['hyphens_or_compounds']} | {c['contractions']} | {c['abbreviations_or_initialisms']} | {c['fillers']} | {e['substitutions']} / {e['deletions']} / {e['insertions']} |")
lines += ['', 'Punctuation and casing cause no remaining edits after the simple normalizer.', 'AMI initialisms such as `X. M. L.` versus `XML` and discarded hesitations explain', 'part of Qwen’s larger simple-WER penalty. The normalized scores reduce that penalty.', '', '## Qwen examples', '', 'Each example shows the reference, output, simple edit count, normalized edit count,', 'and the normalized word diff. `-` marks deleted reference words; `+` marks output words.']
for m in j['models']:
    if m['key'] not in ['qwen4', 'qwen8']:
        continue
    lines += ['', f"### {m['key']}"]
    # Include two normalization-sensitive and three residual-error examples.
    rescued = sorted(m['rows'], key=lambda r:r['simple_errors'] - r['leaderboard_errors'], reverse=True)[:2]
    remaining = [r for r in sorted(m['rows'], key=lambda r:r['leaderboard_errors'], reverse=True) if r['file'] not in {x['file'] for x in rescued}][:3]
    import difflib
    for r in rescued + remaining:
        diff = [x for x in difflib.ndiff(r['leaderboard_reference'].split(), r['leaderboard_hypothesis'].split()) if not x.startswith('  ')]
        lines += ['', f"**{r['file']}** — simple edits {r['simple_errors']}; Open ASR edits {r['leaderboard_errors']}.", '', '- Reference: ' + r['reference'], '- Output: ' + r['hypothesis'], '- Normalized diff: `' + ' | '.join(diff) + '`']
lines += ['', '## Prefix and truncation checks', '', '| Model | Prefix / language-tag matches | Maximum audio s | Maximum output words | >=3 terminal deleted words |', '|---|---:|---:|---:|---:|']
for m in j['models']:
    lines.append(f"| {m['key']} | {len(m['prefix_or_language_tag_candidates'])} | {m['max_audio_s']:.2f} | {m['max_hypothesis_words']} | {len(m['trailing_deletion_candidates'])} |")
lines += ['', 'Qwen produced no detected prefixes or language tags. Neither Qwen variant has a', 'normalized alignment ending in a deletion of three or more reference words.', 'The endpoint sets a 1024 generated-token budget. Output length alone cannot prove', 'that every response ended naturally. `qwen-token-checks.json` checks the longest', 'audio and longest reference directly with the same budget.', '', '## Interpretation', '', 'Normalization explains much of the original Qwen penalty. It does not prove that', 'quantization, runtime differences, or corpus sampling account for the remaining gap.', 'The sample is much smaller than the full leaderboard test sets. A small remaining', 'difference does not establish a general model ranking. Raw rows remain in', '`normalization.json`; no endpoint inference was repeated to change the scores.']
(here / 'normalization.md').write_text('\n'.join(lines) + '\n')
