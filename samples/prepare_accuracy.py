"""Select 200 held-out test-other clips across sorted corpus positions, before inference."""
import json
from pathlib import Path
import subprocess
import tarfile
import wave

here = Path(__file__).resolve().parent
out = here / 'accuracy'
out.mkdir(exist_ok=True)
archive = Path.home() / '.cache/handy-cloud/audio/test-other.tar.gz'
smoke_ids = {x['source_member'] for x in json.loads((here / 'manifest.json').read_text()) if x['group'] == 'test-other'}
with tarfile.open(archive) as tar:
    members = {m.name: m for m in tar.getmembers()}
    candidates = []
    for name in sorted(members):
        if name.endswith('.trans.txt'):
            for line in tar.extractfile(members[name]).read().decode().splitlines():
                clip_id, reference = line.split(' ', 1)
                audio = name.rsplit('/', 1)[0] + '/' + clip_id + '.flac'
                if audio not in smoke_ids:
                    candidates.append((clip_id, reference, audio))
    selected = [candidates[i * len(candidates) // 200] for i in range(200)]
    rows = []
    for clip_id, reference, audio in selected:
        path = out / (clip_id + '.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'pipe:0', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(path)], input=tar.extractfile(members[audio]).read(), check=True)
        with wave.open(str(path)) as wav:
            duration = wav.getnframes() / wav.getframerate()
        rows.append({'file': 'accuracy/' + path.name, 'reference': reference, 'group': 'test-other-200', 'source': 'https://www.openslr.org/resources/12/test-other.tar.gz', 'source_member': audio, 'duration_s': duration})
(here / 'accuracy-manifest.json').write_text(json.dumps(rows, indent=2) + '\n')
print(f'{len(rows)} utterances; {sum(len(x["reference"].split()) for x in rows)} reference words; {sum(x["duration_s"] for x in rows):.1f} seconds')
