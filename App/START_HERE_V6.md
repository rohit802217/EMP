# Version 6

Back up your existing app/data before replacing code. Keep your existing data folder when upgrading.

From the folder containing app.py:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

The six-paper PDF reader uses pypdf and pypdfium2, not PyMuPDF. Scanned documents still require Tesseract. TESSERACT_CMD must point to a real installed tesseract.exe; setting the variable does not install it. CSV/JSON import requires no Tesseract.

Read reviewed_example/RESULTS.md. Your uploaded English response is a duplicate Civil Engineering V sheet. Obtain the correct English response to complete all six papers.

For the supplied reviewed CSVs, choose Manual review / CSV / JSON, select sets B/F/B/J/F for P2/P3/P4/P5/P6 and upload each response/key pair. Leave P1 empty until available. Extract, check the tables, enter confirmed official marking rules, then calculate. Partial results do not save an incomplete record.

Changes: A–L booklet keys supported across pages; duplicate detection; partial calculation; unresolved OCR stays REVIEW; P4 subject corrected; reviewed complete qualified results ranked within the same exam ID, scheme and paper maximums. Ties share competition rank (1,1,3). Imported totals alone do not establish eligibility. An app rank is not an official rank.

Use a consistent exam/recruitment ID for comparable candidates. The administrator must verify subjects and examination. The 30% qualifying threshold, zero floor for negative marks and replacement maximum for deleted questions remain app assumptions; confirm they match your exam before publishing.

The reviewed_example folder contains personal example answers for Rahul Kumar, roll 108430. Remove it before publicly sharing the code.

Tests: `py -m unittest test_scoring_v5 test_v6`.

Validation: all four sets in each of the six supplied keys returned 50 entries (24 sets). Five scoring/ranking tests passed; Streamlit startup passed. OCR of the five valid sheets left 2/6/7/3/5 cells unresolved respectively; all accepted letters matched the visual transcription. Use the reviewed CSVs or correct those REVIEW cells. This validates the supplied layout only, not arbitrary OMR scans.
