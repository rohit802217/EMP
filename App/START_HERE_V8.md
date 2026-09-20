# Version 8 — marksheet and percentages
Stop Streamlit. Back up the app and replace its code, preserving your existing data folder. Run `py -m streamlit run app.py`. The teacher page should say Version 8.

Calculate now displays all six paper rows with scores, maximums, percentages, correct/wrong/unanswered/deleted counts and qualifying status. Missing papers are labeled, never assigned zero. All-six total and percentage appear only for complete results. P3–P6 merit totals remain separate. Complete validated results save automatically. Partial previews remain available for CSV download without publishing. Changes to identity, marking rules or uploads invalidate old results.

Your 04-31 export contains P2=20/50 (40%), P3=30/50 (60%), P4=41/50 (82%), P5=30/50 (60%), P6=37/50 (74%). Merit =138/200 (69%). P1 is absent, so the six-paper total is unavailable. These percentages use your exported scores; they do not independently verify the answer extraction or marking rules.

Complete and partial marksheet rendering were tested, including missing-P1 handling and total calculations.
