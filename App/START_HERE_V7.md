# Version 7: leaderboard update
Stop Streamlit with Ctrl+C. Back up your app folder. Replace the code with this version, preserving your existing data folder. Run `py -m streamlit run app.py` from the updated folder. The teacher page must say Version 7.

Complete reviewed calculations automatically save and rerun the app. A green confirmation identifies the saved roll number. Search/exam filters reset so the new entry is visible in Live Leaderboard. A Refresh leaderboard button reloads saved data. Disqualified candidates now display their earned merit marks but receive no rank.

Missing papers, duplicates, unresolved answers or missing required fields still prevent saving. Follow the displayed error; a partial preview is not a saved result.

Validated: six tests passed, including saving, updating the same roll without duplication, and rendering the saved disqualified candidate's earned marks in the leaderboard. Your running local app has not been accessed; this update must be installed locally.
