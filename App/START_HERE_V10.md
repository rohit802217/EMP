# Version 10 — focused correction and OCR cross-checks
Back up your app and preserve the data folder when replacing code. Run `py -m pip install -r requirements.txt`, then `py -m streamlit run app.py`.

Response summary cells now use three OCR passes, including enlarged and contrast-adjusted images. At least two valid reads must agree with no conflicting valid read. Scanned answer keys use two page segmentation settings; disagreements remain REVIEW. Text PDF keys continue to use direct text extraction and selected booklet filtering. These are correlated Tesseract reads, not independent recognition engines or a guarantee of accuracy.

The editor shows only uncertain questions by default. Show all questions remains available for correcting any accepted error. The confirmation checkbox concerns subjects, booklet sets and marking rules, not repeated inspection of every answer. In-session cached extraction avoids OCR on ordinary reruns. Corrections are not stored across browser sessions; download/save results before closing.

Supported automatic response layout remains the supplied full-page BPSC 50-question printed summary. Arbitrary bubbles, handwritten sheets, rotated/cropped scans and unfamiliar layouts are not certified or universally supported. Use CSV/JSON or manual correction for these. Missing/ambiguous cells never silently become BLANK or zero. Clear structured CSV/JSON data avoids OCR entirely.

The stricter consensus can increase the number of flagged cells. Its purpose is to expose disagreements, not promise fewer uncertain cells on every scan. Nine scoring, persistence, ranking and extraction cross-check tests passed. For the supplied sheets, accepted reads were compared with previously reviewed transcriptions; this is limited sample validation, not a 100% accuracy claim.
