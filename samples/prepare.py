"""Prepare a fixed small smoke-test corpus; this is not a leaderboard evaluation."""
import io
import json
from pathlib import Path
import subprocess
import tarfile
import urllib.request
import wave

HERE = Path(__file__).resolve().parent
CACHE = Path.home() / '.cache/handy-cloud/audio'
CACHE.mkdir(parents=True, exist_ok=True)
rows = []
for split in ('test-clean', 'test-other'):
    url = f'https://www.openslr.org/resources/12/{split}.tar.gz'
    archive = CACHE / f'{split}.tar.gz'
    if not archive.exists():
        urllib.request.urlretrieve(url, archive)
    with tarfile.open(archive) as tar:
        members = {m.name: m for m in tar.getmembers()}
        count = 0
        speakers = set()
        for name in sorted(members):
            if not name.endswith('.trans.txt'):
                continue
            speaker = name.split('/')[-3]
            if speaker in speakers:
                continue
            for line in tar.extractfile(members[name]).read().decode().splitlines():
                clip_id, text = line.split(' ', 1)
                flac_name = name.rsplit('/', 1)[0] + '/' + clip_id + '.flac'
                data = tar.extractfile(members[flac_name]).read()
                output = HERE / f'{split}-{clip_id}.wav'
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'pipe:0', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(output)], input=data, check=True)
                with wave.open(str(output)) as wav:
                    duration = wav.getnframes() / wav.getframerate()
                if not 5 <= duration <= 15:
                    output.unlink()
                    continue
                rows.append({'file': output.name, 'reference': text, 'group': split, 'source': url, 'source_member': flac_name, 'duration_s': duration})
                count += 1
                speakers.add(speaker)
                break
            if count == 5:
                break
        assert count == 5
texts = [
    'Please send the updated meeting notes to the engineering team before Friday afternoon.',
    'The appointment is on Tuesday at nine thirty. Please remind me to bring the signed documents.',
    'I tested the new version this morning and found two issues with the audio settings.',
    'Create a shopping list with apples, brown rice, olive oil, and a loaf of bread.',
    'The server runs on my computer. It keeps the recording private and returns the transcript to the application.',
]
for i, text in enumerate(texts, 1):
    aiff = CACHE / f'dictation-{i:02}.aiff'
    output = HERE / f'dictation-{i:02}.wav'
    subprocess.run(['say', '-v', 'Samantha', '-r', '130', '-o', str(aiff), text], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(aiff), '-af', 'apad=pad_dur=0.5', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(output)], check=True)
    with wave.open(str(output)) as wav:
        duration = wav.getnframes() / wav.getframerate()
    rows.append({'file': output.name, 'reference': text, 'group': 'synthetic-dictation', 'source': 'macOS say; Samantha; 130 words/minute', 'duration_s': duration})
(HERE / 'manifest.json').write_text(json.dumps(rows, indent=2) + '\n')
print(f'Prepared {len(rows)} clips')
