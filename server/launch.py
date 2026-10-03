"""Serve local ASR models; route Phonon to Fermion's loopback-only server."""
from importlib.util import find_spec
from pathlib import Path
import sys

source_path = Path(find_spec('mlx_audio.server').origin)
source = source_path.read_text()
old = 'response_format: str = Form("ndjson")'
assert source.count(old) == 1, 'Review upstream transcription default before upgrading'
source = source.replace(old, 'response_format: str = Form("json")')
import uvicorn
namespace = {'__name__': 'handy_mlx_server', '__file__': str(source_path)}
# Keep this module registered for dataclass and annotation resolution.
import types
module = types.ModuleType(namespace['__name__'])
module.__dict__.update(namespace)
sys.modules[module.__name__] = module
exec(compile(source, str(source_path), 'exec'), module.__dict__)
import httpx
from fastapi.responses import JSONResponse, Response

MODEL_IDS = [
    'mlx-community/parakeet-tdt-0.6b-v3',
    'mlx-community/Qwen3-ASR-1.7B-4bit',
    'mlx-community/Qwen3-ASR-1.7B-8bit',
    'FermionResearch/Phonon-2',
    'mlx-community/granite-speech-4.1-2b-nar-mlx-5bit',
]

@module.app.middleware('http')
async def model_router(request, call_next):
    if request.url.path == '/v1/models' and request.method == 'GET':
        return JSONResponse({'object': 'list', 'data': [{'id': name, 'object': 'model', 'owned_by': 'local'} for name in MODEL_IDS]})
    if request.url.path == '/v1/audio/transcriptions' and request.method == 'POST':
        # Cache bytes before parsing, so the upstream FastAPI handler can read them.
        body = await request.body()
        form = await request.form()
        model = form.get('model')
        import logging
        logging.getLogger('uvicorn.error').info('ASR model=%s file=%s', model, getattr(form.get('file'), 'filename', None))
        if model not in MODEL_IDS:
            return JSONResponse({'error': 'Unknown model; use GET /v1/models'}, status_code=404)
        if model == 'FermionResearch/Phonon-2':
            try:
                async with httpx.AsyncClient(trust_env=False, timeout=300) as client:
                    result = await client.post('http://127.0.0.1:8179/v1/audio/transcriptions', content=body, headers={'Content-Type': request.headers['content-type']})
                return Response(result.content, status_code=result.status_code, media_type=result.headers.get('content-type', 'application/json'))
            except httpx.HTTPError as error:
                return JSONResponse({'error': f'Phonon backend unavailable: {type(error).__name__}'}, status_code=503)
    return await call_next(request)

uvicorn.run(module.app, host='127.0.0.1', port=8178)
