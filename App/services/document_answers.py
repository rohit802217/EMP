"""Readers for BPSC summary sheets and keys; ambiguous cells require review."""
import os
import re
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps
from pypdf import PdfReader
import pypdfium2 as pdfium
import pytesseract

def consensus(values):
    """Agreeing reads are evidence, not a guarantee; disagreements stay unresolved."""
    valid=[v for v in values if v in ('A','B','C','D','*')]
    return valid[0] if len(valid)>=2 and len(set(valid))==1 else 'REVIEW'

def read_cell(cell):
    gray=ImageOps.expand(cell.convert('L'),border=30,fill='white')
    enlarged=gray.resize((gray.width*3,gray.height*3))
    variants=[(gray,10),(enlarged,6),(ImageOps.autocontrast(enlarged),6)]
    votes=[]
    for variant,psm in variants:
        config=f'--psm {psm}'+(' -c tessedit_char_whitelist=ABCD*' if psm==10 else '')
        text=pytesseract.image_to_string(variant,config=config,timeout=15).strip()
        votes.append(text[0] if re.fullmatch(r'[ABCD*][.,;:]?',text) else '')
    return consensus(votes)


def setup_ocr():
    executable = os.environ.get('TESSERACT_CMD')
    if not executable and os.name == 'nt':
        candidate = Path(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        if candidate.exists():
            executable = str(candidate)
    if executable:
        pytesseract.pytesseract.tesseract_cmd = executable


def render(data, page=0):
    doc = pdfium.PdfDocument(data)
    try:
        p = doc[page]
        bitmap = p.render(scale=300/72)
        im = bitmap.to_pil().copy()
        bitmap.close()
        p.close()
        return im
    finally:
        doc.close()


def _read_key(data, name, series, psm=6):
    used_ocr=False
    if name.lower().endswith('.pdf'):
        pages = PdfReader(BytesIO(data)).pages
        texts = []
        for index, page in enumerate(pages):
            text = page.extract_text(extraction_mode='layout') or ''
            if len(re.findall(r'\b\d+\s+(?:[ABCD]|Deleted)\b', text, re.I)) < 3:
                setup_ocr()
                used_ocr=True
                text = pytesseract.image_to_string(render(data, index), config=f'--psm {psm}',timeout=90)
            texts.append(text)
        text = '\n'.join(texts)
    else:
        setup_ocr()
        used_ocr=True
        text = pytesseract.image_to_string(Image.open(BytesIO(data)), config=f'--psm {psm}',timeout=90)
    chunks = re.split(r'\(?\bSet\s*[-–—:]?\s*([A-L])\b\s*\)?', text, flags=re.I)
    if len(chunks) > 1:
        text = '\n'.join(chunks[i+1] for i in range(1, len(chunks)-1, 2) if chunks[i].upper() == series)
        if not text:
            raise ValueError(f'Set {series} was not found in the answer key.')
    answers = {}
    for q, answer in re.findall(r'\b(\d{1,3})\s+(Deleted|[ABCD])\b', text, re.I):
        q, answer = int(q), answer.upper()
        if q in answers and answers[q] != answer:
            raise ValueError(f'Conflicting key entries for question {q}; review booklet set.')
        answers[q] = answer
    return answers,used_ocr

def read_key(data,name,series):
    first,used_ocr=_read_key(data,name,series)
    if not used_ocr:
        return first
    second,_=_read_key(data,name,series,psm=3)
    return {q:first[q] if q in first and first[q]==second.get(q) else 'REVIEW'
            for q in set(first)|set(second)}


def read_bpsc_summary(data, name, series):
    """Template for the supplied full-page BPSC 50-question portal export.

    Coordinates describe the printed response summary, not bubble marks.
    Any other layout must use manual review/import instead of guessed marks.
    """
    setup_ocr()
    im = render(data) if name.lower().endswith('.pdf') else Image.open(BytesIO(data)).convert('RGB')
    w, h = im.size
    header = pytesseract.image_to_string(im.crop((0, int(h*.66), w, int(h*.737))), config='--psm 6')
    found = re.search(r'BOOKLET\s+SERIES\s*[:：]?\s*([A-L])\b', header, re.I)
    if not found:
        raise ValueError('BPSC response-summary layout not recognized. Use the manual/CSV option.')
    if found[1].upper() != series:
        raise ValueError(f'Response sheet is Set {found[1].upper()}, but Set {series} was selected.')
    answers = {}
    for row, (top, bottom) in enumerate(((.752,.768),(.787,.803))):
        for i in range(25):
            x = (.056 + (.921-.056)*i/24)*w
            cell = im.crop((int(x-w*.014),int(h*top),int(x+w*.014),int(h*bottom))).convert('L')
            value = read_cell(cell)
            # Empty OCR is NOT evidence that the candidate left the answer blank.
            answers[row*25+i+1] = value if value in ('A','B','C','D','*') else 'REVIEW'
    return answers
