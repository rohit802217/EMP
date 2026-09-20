# Version 5: six-paper evaluation

Keep your existing data folder backed up. Replace application code and install:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

The teacher page must display **Version 5**. Upload each response and matching key under its paper. Select the booklet series separately for every paper. Select the BPSC template only for full-page exports matching the supplied 5.pdf (two horizontal summary rows of 25 responses). Other layouts require manual review or CSV/JSON. This is not a universal bubble detector.

Click Extract all six papers. Correct every REVIEW cell and inspect every OCR answer. BLANK is an explicit unanswered response; * means multiple marks. The key reader keeps I/J/K/L separate across page breaks and imports Deleted automatically. Additional deleted numbers must exist in the key.

Verify subject, exam and booklet against the source documents. Handwritten subject names are not automatically validated. Confirm the marking rules and review checkbox, then calculate/save. All six papers must pass validation before anything is saved. P1/P2 require 30%; only qualified candidates get merit ranks. Export the combined CSV or use Direct Result Lookup.

Defaults (+1 correct, -1 wrong, +2 deleted) are not confirmed official rules. Unanswered scores zero; negative totals are floored at zero. Maximum is nondeleted question count times correct marks plus deleted count times deleted marks. Confirm this policy matches your exam before publishing.

## Windows OCR

The new BPSC reader uses pypdfium2 to render PDFs; it does not require PyMuPDF or Poppler. Text keys use pypdf. Image responses still need the Tesseract executable. Install Tesseract and put it on PATH, or use its standard installation at C:\Program Files\Tesseract-OCR\tesseract.exe. For another location set TESSERACT_CMD before launching the app. The Python pytesseract package alone is not the OCR executable.

The original comparison page's OCR service still uses pdf2image/Poppler; the new teacher page does not use that route for PDFs.

## Validation scope

Tested against supplied Civil Engineering Paper V Set J key and response summary. Other five actual response/key pairs have not been supplied. OCR may leave cells for manual review. Keep old zero-score records under review until reevaluated; the update does not delete them.
