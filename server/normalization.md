# Normalization and Qwen error checks

Observed scores use the exact pinned Open ASR Leaderboard `EnglishTextNormalizer`.
https://github.com/huggingface/open_asr_leaderboard/blob/67e8bd6acea240819ad67080f6f31e15d4a90da5/normalizer/normalizer.py

The first benchmark used lowercase text and punctuation removal. It did not expand
numbers, contractions, fillers, or compound words. This penalized Qwen formatting.
Verbatim WER also preserves reference casing. LibriSpeech and AMI use uppercase
references. Verbatim WER is reported for completeness; it is not a useful ranking.

## Per-set scores

| Model | Set | Verbatim WER | Simple WER | Open ASR WER | Open ASR edits / words |
|---|---|---:|---:|---:|---:|
| parakeet | ami-ihm-100 | 98.69% | 10.17% | 8.71% | 188 / 2159 |
| parakeet | synthetic-dictation | 5.19% | 2.60% | 1.32% | 1 / 76 |
| parakeet | test-clean | 100.00% | 0.80% | 0.80% | 1 / 125 |
| parakeet | test-other | 98.48% | 1.52% | 1.49% | 2 / 134 |
| parakeet | test-other-200 | 98.20% | 3.37% | 3.25% | 111 / 3419 |
| qwen4 | ami-ihm-100 | 98.46% | 14.37% | 9.40% | 203 / 2159 |
| qwen4 | synthetic-dictation | 2.60% | 2.60% | 2.63% | 2 / 76 |
| qwen4 | test-clean | 100.00% | 2.40% | 0.80% | 1 / 125 |
| qwen4 | test-other | 98.48% | 6.82% | 0.75% | 1 / 134 |
| qwen4 | test-other-200 | 98.25% | 4.17% | 3.57% | 122 / 3419 |
| qwen8 | ami-ihm-100 | 98.37% | 13.57% | 8.89% | 192 / 2159 |
| qwen8 | synthetic-dictation | 2.60% | 2.60% | 2.63% | 2 / 76 |
| qwen8 | test-clean | 100.00% | 3.20% | 0.00% | 0 / 125 |
| qwen8 | test-other | 98.48% | 6.06% | 0.75% | 1 / 134 |
| qwen8 | test-other-200 | 98.31% | 3.96% | 3.28% | 112 / 3419 |
| phonon | ami-ihm-100 | 98.41% | 10.07% | 8.34% | 180 / 2159 |
| phonon | synthetic-dictation | 0.00% | 0.00% | 0.00% | 0 / 76 |
| phonon | test-clean | 100.00% | 0.80% | 0.80% | 1 / 125 |
| phonon | test-other | 98.48% | 3.03% | 2.99% | 4 / 134 |
| phonon | test-other-200 | 98.22% | 4.23% | 4.01% | 137 / 3419 |
| granite | ami-ihm-100 | 101.26% | 8.16% | 7.74% | 167 / 2159 |
| granite | synthetic-dictation | 14.29% | 2.60% | 1.32% | 1 / 76 |
| granite | test-clean | 100.00% | 0.00% | 0.00% | 0 / 125 |
| granite | test-other | 100.00% | 0.00% | 0.00% | 0 / 134 |
| granite | test-other-200 | 100.12% | 2.63% | 2.54% | 87 / 3419 |

## Error categories

Counts below flag clips whose edit count decreased after Open ASR normalization.
Flags overlap. They use text-pattern heuristics. They do not attribute each edit.
Residual edit counts come from exact normalized word alignment.
A residual edit can still reflect reference conventions or a reference error.

| Model | Numbers/titles | Hyphens/compounds | Contractions | Abbreviations | Fillers | Residual S / D / I |
|---|---:|---:|---:|---:|---:|---:|
| parakeet | 1 | 0 | 12 | 8 | 12 | 186 / 76 / 41 |
| qwen4 | 8 | 8 | 29 | 7 | 34 | 185 / 114 / 30 |
| qwen8 | 2 | 11 | 27 | 7 | 33 | 169 / 110 / 28 |
| phonon | 1 | 0 | 12 | 7 | 12 | 201 / 75 / 46 |
| granite | 1 | 1 | 9 | 0 | 8 | 159 / 53 / 43 |

Punctuation and casing cause no remaining edits after the simple normalizer.
AMI initialisms such as `X. M. L.` versus `XML` and discarded hesitations explain
part of Qwen’s larger simple-WER penalty. The normalized scores reduce that penalty.

## Qwen examples

Each example shows the reference, output, simple edit count, normalized edit count,
and the normalized word diff. `-` marks deleted reference words; `+` marks output words.

### qwen4

**meeting/AMI_EN2002b_H03_MEE073_0141101_0141775.wav** — simple edits 10; Open ASR edits 2.

- Reference: FLIP IT INTO UH YEAH JUST UH TRANSFORMS UM LIKE UM STYLE SHEET THE UM X. M. L. STYLE SHEET
- Output: Flip it into, just transforms, like style sheet, XML, style sheet.
- Normalized diff: `- yeah | - the`

**meeting/AMI_EN2002c_H02_MEE071_0279167_0279738.wav** — simple edits 8; Open ASR edits 2.

- Reference: BUT YOU HAVE NO RANKING SYSTEM AT THE MOMENT SO IF SOMETHING'S AN AMAZING W HIGHLY RANKED THING FROM T. F. I. D. F.
- Output: But you have no ranking system at the moment, so if something is an amazing, highly ranked thing from TFIDF.
- Normalized diff: `- s | + is | - w`

**accuracy/2609-169640-0000.wav** — simple edits 10; Open ASR edits 10.

- Reference: PROAS IN THAT QUARTER WERE USUALLY DISTRUSTED BY SHIPS IT IS TRUE BUT THE SEA IS FULL OF THEM AND FAR MORE ARE INNOCENT THAN ARE GUILTY OF ANY ACTS OF VIOLENCE
- Output: Perots in that quarter were usually distracted by the ships at issue, but the Cs four of them, far more are innocent than are guilty of any acts of violence.
- Normalized diff: `- proas | + perots | - distrusted | ?      ^^
 | + distracted | ?      ^^
 | + the | + at | + issue | - it | - is | - true | + cs | + 4 | - sea | - is | - full | - and`

**meeting/AMI_EN2002a_H03_MEE071_0130698_0131380.wav** — simple edits 7; Open ASR edits 7.

- Reference: FOUR AND IT W IT LI IT JUST HAS AN OPEN VARIABLE TRANSPARENT S LIST WHATEVER FIND EVERYTHING THAT'S GOT THAT AND THEN LOAD
- Output: Four and it what like it just has an open variable transport this whatever, find everything that's got that and then like.
- Normalized diff: `+ what | + like | - w | - it | - li | - transparent | ?       ^ --
 | + transport | ?       ^
 | + this | - s | - list | - load | + like`

**accuracy/3005-163390-0015.wav** — simple edits 6; Open ASR edits 6.

- Reference: AND LOOK AT CHARLES SECOND AND LOUIS FOURTEEN AND LOUIS FIFTEEN AND JAMES SECOND AND EDWARD SECOND AND RICHARD THIRD AND FORTY MORE BESIDES ALL THEM SAXON HEPTARCHIES THAT USED TO RIP AROUND SO IN OLD TIMES AND RAISE CAIN
- Output: And look at Charles II, and Louis XIV, and Louis XV, and James II, and Edward II, and Richard III, and forty more, besides all them Saxon heptarchies that used to rip around so in old times and raise Cain.
- Normalized diff: `- 2nd | + ii | - 14 | + xiv | - 15 | + xv | - 2nd | + ii | - 2nd | + ii | - 3rd | + iii`

### qwen8

**meeting/AMI_EN2002b_H03_MEE073_0141101_0141775.wav** — simple edits 10; Open ASR edits 2.

- Reference: FLIP IT INTO UH YEAH JUST UH TRANSFORMS UM LIKE UM STYLE SHEET THE UM X. M. L. STYLE SHEET
- Output: Flip it into just transforms like style sheet XML style sheet.
- Normalized diff: `- yeah | - the`

**meeting/AMI_EN2002a_H02_FEO072_0122961_0124017.wav** — simple edits 6; Open ASR edits 1.

- Reference: IT WAS THERE WHEN I TOOK IT UM USES THE UM THE N. X. T. SEARCH TO GET THE DATA OUT OF THE OUT THE FILES
- Output: It was there when I took it. Uses the the NXT search to get the data out of the out of the files.
- Normalized diff: `+ of`

**accuracy/2609-169640-0000.wav** — simple edits 6; Open ASR edits 6.

- Reference: PROAS IN THAT QUARTER WERE USUALLY DISTRUSTED BY SHIPS IT IS TRUE BUT THE SEA IS FULL OF THEM AND FAR MORE ARE INNOCENT THAN ARE GUILTY OF ANY ACTS OF VIOLENCE
- Output: Pirats in that quarter were usually distracted by the ships. It is true, but the sea has fooled them, and far more are innocent than are guilty of any acts of violence.
- Normalized diff: `- proas | + pirats | - distrusted | ?      ^^
 | + distracted | ?      ^^
 | + the | + has | + fooled | - is | - full | - of`

**accuracy/3005-163390-0015.wav** — simple edits 6; Open ASR edits 6.

- Reference: AND LOOK AT CHARLES SECOND AND LOUIS FOURTEEN AND LOUIS FIFTEEN AND JAMES SECOND AND EDWARD SECOND AND RICHARD THIRD AND FORTY MORE BESIDES ALL THEM SAXON HEPTARCHIES THAT USED TO RIP AROUND SO IN OLD TIMES AND RAISE CAIN
- Output: And look at Charles II, and Louis XIV, and Louis XV, and James II, and Edward II, and Richard III, and forty more, besides all them Saxon heptarchies that used to rip around so in old times and raise Cain.
- Normalized diff: `- 2nd | + ii | - 14 | + xiv | - 15 | + xv | - 2nd | + ii | - 2nd | + ii | - 3rd | + iii`

**meeting/AMI_EN2002a_H03_MEE071_0130698_0131380.wav** — simple edits 6; Open ASR edits 6.

- Reference: FOUR AND IT W IT LI IT JUST HAS AN OPEN VARIABLE TRANSPARENT S LIST WHATEVER FIND EVERYTHING THAT'S GOT THAT AND THEN LOAD
- Output: Four and it what like it just has an open variable transport this whatever find everything that's got that and then load.
- Normalized diff: `+ what | + like | - w | - it | - li | - transparent | ?       ^ --
 | + transport | ?       ^
 | + this | - s | - list`

## Prefix and truncation checks

| Model | Prefix / language-tag matches | Maximum audio s | Maximum output words | >=3 terminal deleted words |
|---|---:|---:|---:|---:|
| parakeet | 0 | 26.09 | 69 | 1 |
| qwen4 | 0 | 26.09 | 69 | 0 |
| qwen8 | 0 | 26.09 | 69 | 0 |
| phonon | 0 | 26.09 | 69 | 1 |
| granite | 0 | 26.09 | 69 | 0 |

Qwen produced no detected prefixes or language tags. Neither Qwen variant has a
normalized alignment ending in a deletion of three or more reference words.
The endpoint sets a 1024 generated-token budget. Output length alone cannot prove
that every response ended naturally. `qwen-token-checks.json` checks the longest
audio and longest reference directly with the same budget.

## Interpretation

Normalization explains much of the original Qwen penalty. It does not prove that
quantization, runtime differences, or corpus sampling account for the remaining gap.
The sample is much smaller than the full leaderboard test sets. A small remaining
difference does not establish a general model ranking. Raw rows remain in
`normalization.json`; no endpoint inference was repeated to change the scores.
