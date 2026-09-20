# Version 9 — table totals and result certificate
Preserve your existing data folder when replacing code. Restart with `py -m streamlit run app.py` and confirm Version 9 on the teacher page.

The existing paper table now includes QUALIFYING TOTAL, MERIT TOTAL and GRAND TOTAL rows. English and Hindi must each meet the configured qualifying percentage (currently 30%). Passing one cannot compensate for failing the other. P3–P6 alone determine merit; grand total is informational. Overall PASS means qualifying eligibility, not final selection. Missing papers give PENDING and no certificate.

Complete calculated results offer a printable HTML result certificate with name, roll, exam, paper scores, totals, percentages and PASS/FAIL. Download, open in a browser, and choose Print / Save as PDF. It is labeled as an app-generated statement, not an official certificate. Complete validated results still save automatically to the leaderboard.

Validated totals, PASS/FAIL, incomplete-result behavior, escaped certificate text and six existing scoring/save/ranking tests.
