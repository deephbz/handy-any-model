"""Rescore saved hypotheses with the pinned Open ASR Leaderboard English normalizer."""
import argparse
import difflib
import importlib
import json
from pathlib import Path
import re
import sys

import jiwer
import requests

ROOT = Path(__file__).resolve().parent.parent
REVISION = '67e8bd6acea240819ad67080f6f31e15d4a90da5'
CACHE = Path.home() / '.cache/handy-cloud/normalizers'
PACKAGE = CACHE / 'leaderboard_normalizer'
PACKAGE.mkdir(parents=True, exist_ok=True)
(PACKAGE / '__init__.py').touch()
for filename in ['normalizer.py', 'english_abbreviations.py']:
    path = PACKAGE / filename
    if not path.exists():
        url = f'https://raw.githubusercontent.com/huggingface/open_asr_leaderboard/{REVISION}/normalizer/{filename}'
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        path.write_text(response.text)
sys.path.insert(0, str(CACHE))
normalizer_module = importlib.import_module('leaderboard_normalizer.normalizer')
EnglishTextNormalizer = normalizer_module.EnglishTextNormalizer
normalize = EnglishTextNormalizer()
keys = ['parakeet', 'qwen4', 'qwen8', 'phonon', 'granite']
records = []
for key in keys:
    per_set = {}
    examples = []
    categories = {'numbers_or_titles': 0, 'hyphens_or_compounds': 0, 'contractions': 0, 'abbreviations_or_initialisms': 0, 'fillers': 0, 'punctuation_or_case_after_simple_normalization': 0}
    all_rows = []
    for kind in ['smoke', 'accuracy', 'meeting']:
        path = ROOT / f'server/benchmarks/{key}-{kind}.json'
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for row in data['rows']:
            ref, hyp = normalize(row['reference']).strip(), normalize(row['hypothesis']).strip()
            alignment = jiwer.process_words(ref, hyp)
            errors = alignment.substitutions + alignment.deletions + alignment.insertions
            verbatim = jiwer.process_words(row['reference'], row['hypothesis'])
            raw_errors = verbatim.substitutions + verbatim.deletions + verbatim.insertions
            simple_errors = row['substitutions'] + row['deletions'] + row['insertions']
            scored = {'file': row['file'], 'group': row['group'], 'duration_s': row['duration_s'], 'reference': row['reference'], 'hypothesis': row['hypothesis'], 'leaderboard_reference': ref, 'leaderboard_hypothesis': hyp, 'leaderboard_errors': errors, 'leaderboard_words': len(ref.split()), 'substitutions': alignment.substitutions, 'deletions': alignment.deletions, 'insertions': alignment.insertions, 'simple_errors': simple_errors, 'simple_words': row['reference_words'], 'verbatim_errors': raw_errors, 'verbatim_words': len(row['reference'].split())}
            all_rows.append(scored)
            source = row['reference'] + ' ' + row['hypothesis']
            if errors < simple_errors:
                if re.search(r'\d|\b[IVX]{2,}\b|\b(?:second|third|fourteen|fifteen|mister|saint)\b', source, re.I): categories['numbers_or_titles'] += 1
                if '-' in source or any(re.search(pattern, source, re.I) for pattern in normalizer_module.english_compound_normalizer): categories['hyphens_or_compounds'] += 1
                if "'" in source: categories['contractions'] += 1
                if re.search(r'\b[A-Z](?:\.|[A-Z])', row['hypothesis']): categories['abbreviations_or_initialisms'] += 1
                if re.search(normalize.ignore_patterns, source, re.I): categories['fillers'] += 1
            if simple_errors or errors:
                scored['diff'] = [x for x in difflib.ndiff(ref.split(), hyp.split()) if not x.startswith('  ')]
                examples.append(scored)
    if not all_rows:
        continue
    for group in sorted({r['group'] for r in all_rows}):
        rows = [r for r in all_rows if r['group'] == group]
        per_set[group] = {}
        for stage in ['verbatim', 'simple', 'leaderboard']:
            errors = sum(r[stage + '_errors'] for r in rows)
            words = sum(r[stage + '_words'] for r in rows)
            per_set[group][stage] = {'errors': errors, 'words': words, 'wer': errors / words}
    total = {}
    for stage in ['verbatim', 'simple', 'leaderboard']:
        errors = sum(r[stage + '_errors'] for r in all_rows)
        words = sum(r[stage + '_words'] for r in all_rows)
        total[stage] = {'errors': errors, 'words': words, 'wer': errors / words}
    prefix_candidates = [r['file'] for r in all_rows if re.match(r'\s*(?:<|\[|language\s*:|english\s*:|transcription\s*:|transcript\s*:)', r['hypothesis'], re.I)]
    trailing_deletions = []
    for r in all_rows:
        alignment = jiwer.process_words(r['leaderboard_reference'], r['leaderboard_hypothesis'])
        last = alignment.alignments[0][-1]
        if last.type == 'delete' and last.ref_end_idx - last.ref_start_idx >= 3:
            trailing_deletions.append({'file': r['file'], 'duration_s': r['duration_s'], 'missing_words': r['leaderboard_reference'].split()[last.ref_start_idx:last.ref_end_idx]})
    records.append({'key': key, 'per_set': per_set, 'total': total, 'normalization_sensitive_clip_flags': categories, 'category_definition': 'Overlapping heuristic flags on clips whose edit count decreases with leaderboard normalization. These counts do not uniquely attribute word errors.', 'residual_edits': {k: sum(r[k] for r in all_rows) for k in ['substitutions', 'deletions', 'insertions']}, 'prefix_or_language_tag_candidates': prefix_candidates, 'trailing_deletion_candidates': trailing_deletions, 'max_audio_s': max(r['duration_s'] for r in all_rows), 'max_hypothesis_words': max(len(r['hypothesis'].split()) for r in all_rows), 'examples': sorted(examples, key=lambda r: (r['simple_errors'] - r['leaderboard_errors'], r['leaderboard_errors']), reverse=True)[:10], 'rows': all_rows})
result = {'normalizer_source': f'https://github.com/huggingface/open_asr_leaderboard/blob/{REVISION}/normalizer/normalizer.py', 'normalizer': 'EnglishTextNormalizer; default publisher mappings; strip', 'verbatim_definition': 'case-sensitive whitespace word WER; uppercase corpus references make it unsuitable for recognition ranking', 'simple_definition': 'original lowercase + remove punctuation + collapse whitespace scoring', 'models': records}
(ROOT / 'server/normalization.json').write_text(json.dumps(result, indent=2) + '\n')
for r in records:
    print(r['key'], r['total'], r['residual_edits'])
