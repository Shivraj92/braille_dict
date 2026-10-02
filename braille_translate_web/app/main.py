from pathlib import Path
import os, tempfile
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .braille_service import BrailleTranslator

BASE=Path(__file__).resolve().parent.parent
UPLOADS=BASE/'uploads'; UPLOADS.mkdir(exist_ok=True)
app=FastAPI(title='Braille Translate', version='1.0')
app.mount('/static', StaticFiles(directory=BASE/'static'), name='static')
templates=Jinja2Templates(directory=BASE/'templates')
translator=BrailleTranslator()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/api/tables')
async def tables():
    return {'tables': translator.list_table_files()}

@app.post('/api/translate')
async def translate(text: str=Form(''), language: str=Form('en'), grade: str=Form('1'), region: str=Form(''), encoding: str=Form('unicode'), ocr_language: str=Form('eng'), file: UploadFile|None=File(None)):
    tmp=None
    try:
        source=text.strip(); filename=None
        if file and file.filename:
            filename=file.filename
            suffix=Path(file.filename).suffix.lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=UPLOADS) as f:
                f.write(await file.read()); tmp=f.name
            source=translator.extract_text(tmp, ocr_language).strip()
        if not source: return JSONResponse({'error':'Enter text or upload a supported file.'}, status_code=400)
        result=translator.translate(source, language, grade, region, encoding)
        return {'source_text':source,'braille':result,'language':language,'grade':grade,'encoding':encoding,'filename':filename}
    except Exception as e:
        return JSONResponse({'error':str(e)}, status_code=400)
    finally:
        if tmp:
            try: os.remove(tmp)
            except OSError: pass
