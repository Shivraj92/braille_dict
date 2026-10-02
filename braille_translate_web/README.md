# Braille Translate Web

PyCharm-friendly multilingual Braille translation website built around Liblouis.

Features:
- Text to Braille using Liblouis tables
- Grade 1 uncontracted and Grade 2 contracted modes
- Language and optional region selection
- Unicode Braille, dot-number and ASCII-safe output
- TXT, PDF and common image uploads
- OCR for photos and scanned PDFs using Tesseract
- Responsive browser interface

## Run

Use Python 3.11:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

For image/scanned-PDF OCR, install Tesseract OCR separately and put it on PATH.

Liblouis supplies the translation tables; the app does not use a small hard-coded alphabet map. Its tables support literary/computer Braille and contracted/uncontracted translation for many languages. See the official Liblouis repository: https://github.com/liblouis/liblouis
