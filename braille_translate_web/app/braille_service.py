from pathlib import Path
import os

try:
    import louis
except ImportError:
    louis = None

class BrailleTranslator:
    def _find_tables(self, query: str):
        if louis is not None:
            for name in ('findTables', 'findTable'):
                fn = getattr(louis, name, None)
                if fn:
                    try:
                        result = fn(query)
                        return [result] if isinstance(result, str) else list(result or [])
                    except Exception:
                        pass
        return []

    def resolve_table(self, language='en', grade='1', region=''):
        query = f'language:{language.lower()} grade:{grade}'
        if region:
            query += f' region:{region.lower()}'
        tables = self._find_tables(query)
        if tables:
            return tables
        if language.lower() in ('en', 'eng', 'english'):
            return ['en-us-g1.ctb' if grade == '1' else 'en-us-g2.ctb']
        raise RuntimeError(f'No Liblouis table found for {query}')

    def translate(self, text, language='en', grade='1', region='', encoding='unicode'):
        if louis is None:
            raise RuntimeError('Install the Liblouis Python bindings: pip install louis')
        tables = self.resolve_table(language, grade, region)
        try:
            result = louis.translateString(tables, text)
        except TypeError:
            result = louis.translateString(','.join(tables), text)
        if encoding == 'unicode':
            return result
        if encoding == 'dots':
            return self.to_dot_numbers(result)
        if encoding == 'ascii':
            return ' '.join(f'U+{ord(c):04X}' if 0x2800 <= ord(c) <= 0x28FF else c for c in result)
        raise ValueError('Unknown encoding')

    @staticmethod
    def to_dot_numbers(text):
        out=[]
        for c in text:
            n=ord(c)
            if 0x2800 <= n <= 0x28FF:
                mask=n-0x2800
                dots=''.join(str(i+1) for i in range(8) if mask & (1<<i))
                out.append(dots or '0')
            else:
                out.append(c)
        return ' '.join(out)

    @staticmethod
    def extract_text(path, ocr_language='eng'):
        suffix=Path(path).suffix.lower()
        if suffix in {'.txt','.md','.csv','.json','.xml','.html','.py'}:
            return Path(path).read_text(encoding='utf-8', errors='ignore')
        if suffix == '.pdf':
            from pypdf import PdfReader
            text='\n'.join(page.extract_text() or '' for page in PdfReader(path).pages)
            if text.strip(): return text
            import fitz, io, pytesseract
            from PIL import Image
            doc=fitz.open(path); pages=[]
            for page in doc:
                pix=page.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False)
                pages.append(pytesseract.image_to_string(Image.open(io.BytesIO(pix.tobytes('png'))), lang=ocr_language))
            return '\n'.join(pages)
        if suffix in {'.png','.jpg','.jpeg','.webp','.bmp','.tif','.tiff'}:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(path), lang=ocr_language)
        raise ValueError('Unsupported file type')

    def list_table_files(self):
        roots=[Path(p) for p in os.getenv('LOUIS_TABLEPATH','').split(os.pathsep) if p]
        result=[]
        for root in roots:
            if root.exists(): result.extend(p.name for p in root.glob('*.ctb'))
        return sorted(set(result))
