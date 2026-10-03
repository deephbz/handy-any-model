"""Verify each model through curl at the public contract endpoint."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time

here = Path(__file__).resolve().parent
url = 'http://127.0.0.1:8178'
listing = json.loads(subprocess.check_output(['curl', '-fsS', url + '/v1/models']))
checks = []
expected = 'please send the updated meeting notes to the engineering team before friday afternoon'
for item in listing['data']:
    command = ['curl', '-sS', '--max-time', '300', '-w', '\n%{http_code}', '-H', 'Authorization: Bearer dummy', '-F', 'file=@' + str(here.parent / 'samples/dictation-01.wav'), '-F', 'model=' + item['id'], url + '/v1/audio/transcriptions']
    start = time.perf_counter()
    response = subprocess.check_output(command, text=True)
    elapsed = time.perf_counter() - start
    body, status = response.rsplit('\n', 1)
    payload = json.loads(body)
    assert status == '200', (item, payload)
    assert payload['text'].lower().strip().rstrip('.') == expected, (item, payload)
    checks.append({'model': item['id'], 'status': int(status), 'elapsed_s': elapsed, 'response': payload, 'response_format': 'omitted', 'bearer_key': 'dummy', 'client': 'curl'})
invalid = subprocess.check_output(['curl', '-sS', '-w', '\n%{http_code}', '-F', 'file=@' + str(here.parent / 'samples/dictation-01.wav'), '-F', 'model=invalid-model', url + '/v1/audio/transcriptions'], text=True)
assert invalid.rsplit('\n', 1)[1] == '404'
(here / 'endpoint-checks.json').write_text(json.dumps({'created_at': datetime.now(timezone.utc).isoformat(), 'model_listing': listing, 'checks': checks, 'unknown_model_status': 404}, indent=2) + '\n')
print('Verified curl text and HTTP 200 for all five models; unknown model returns 404.')
