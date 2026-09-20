# 6-Paper OMR Evaluation & Result Portal

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

For OCR of images and scanned PDFs, install Tesseract and Poppler on the host.
The included `packages.txt` installs both automatically on Streamlit Community Cloud.
Text PDFs, CSV and JSON files do not require the external Tesseract executable.

Set the teacher/admin password before deployment:

```bash
export EXAM_APP_ADMIN_PASSWORD="a-strong-private-password"
```

On Windows PowerShell:

```powershell
$env:EXAM_APP_ADMIN_PASSWORD="a-strong-private-password"
```

## Supported answer formats

- CSV: two columns such as `question,answer`
- JSON object: `{"1":"A","2":"C"}` or `{"answers":{"1":"A"}}`
- JSON list: `[{"question":1,"answer":"A"}]`
- PDF/JPG/JPEG/PNG: OCR text such as `1 A`, `Q2: C`, one answer per line

The teacher page requires response and answer-key files for P1 through P6. P1 and P2 are qualifying papers (30% minimum by default); P3-P6 determine merit only when both qualifying papers are passed. Deleted questions receive the configured bonus.

Candidate results can be shared with a URL such as:

`https://your-app.streamlit.app/?roll_no=648484`

Do not rely on the bundled development password in production. Configure `EXAM_APP_ADMIN_PASSWORD` in Streamlit secrets/environment settings.
