"""Prepare 100 fixed AMI headset meeting clips from one public test shard."""
import json
from pathlib import Path
import subprocess
import urllib.request
import wave
import pyarrow.parquet as pq

here = Path(__file__).resolve().parent
out = here / 'meeting'
out.mkdir(exist_ok=True)
cache = Path.home() / '.cache/handy-cloud/audio/ami-ihm-test-00000.parquet'
url = 'https://huggingface.co/datasets/edinburghcstr/ami/resolve/main/ihm/test-00000-of-00004.parquet'
if not cache.exists():
    urllib.request.urlretrieve(url, cache)
meta = pq.read_table(cache, columns=['text', 'begin_time', 'end_time', 'audio_id', 'meeting_id', 'speaker_id']).to_pylist()
candidates = [i for i, r in enumerate(meta) if 5 <= r['end_time'] - r['begin_time'] <= 15 and len(r['text'].split()) >= 8]
assert len(candidates) >= 100
indices = [candidates[i * len(candidates) // 100] for i in range(100)]
audio = pq.read_table(cache, columns=['audio'])['audio']
rows = []
for index in indices:
    r = meta[index]
    path = out / (r['audio_id'] + '.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'pipe:0', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(path)], input=audio[index].as_py()['bytes'], check=True)
    with wave.open(str(path)) as wav:
        duration = wav.getnframes() / wav.getframerate()
    rows.append({'file': 'meeting/' + path.name, 'reference': r['text'], 'group': 'ami-ihm-100', 'source': url, 'source_row': index, 'meeting_id': r['meeting_id'], 'speaker_id': r['speaker_id'], 'duration_s': duration})
(here / 'meeting-manifest.json').write_text(json.dumps(rows, indent=2) + '\n')
print(f'{len(rows)} clips, {sum(len(x["reference"].split()) for x in rows)} words; meetings: {sorted({x["meeting_id"] for x in rows})}')
