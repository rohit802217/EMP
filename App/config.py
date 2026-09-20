"""
Central configuration for the app.

Every other module should import paths and constants from here
instead of hardcoding them, so the folder layout only has to be
defined in one place.
"""

import os

# ------------------------------------------------------------------
# Base paths
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, "leaderboard.json")
VACANCY_FILE = os.path.join(DATA_DIR, "vacancies.json")

# ------------------------------------------------------------------
# App-wide constants
# ------------------------------------------------------------------

PAGE_TITLE = "6-Paper OMR Evaluation & Result Portal"
PAGE_ICON = "📝"

# Merit score is out of 4 papers (P3-P6) x 100 marks each
MAX_MERIT_TOTAL = 400
PASS_MARK = 30  # minimum marks to pass P1 (English) / P2 (Hindi)

VALID_ANSWER_OPTIONS = ["A", "B", "C", "D"]
VALID_ANSWER_OPTIONS_WITH_DELETED = ["A", "B", "C", "D", "DELETED"]

# ------------------------------------------------------------------
# Admin access
# ------------------------------------------------------------------
# Change this, or better: set an environment variable before running
# the app: setx EXAM_APP_ADMIN_PASSWORD "your-password"  (Windows)
# or       export EXAM_APP_ADMIN_PASSWORD="your-password" (Linux/Mac)
ADMIN_PASSWORD = os.environ.get("EXAM_APP_ADMIN_PASSWORD", "admin123")

# Six-paper examination structure. P1/P2 are qualifying papers and P3-P6
# determine merit only after both qualifying papers are passed.
PAPERS = {
    "p1": {"code": "P1", "subject": "English", "category": "Qualifying", "max_marks": 100},
    "p2": {"code": "P2", "subject": "Hindi", "category": "Qualifying", "max_marks": 100},
    "p3": {"code": "P3", "subject": "General Studies I", "category": "Merit", "max_marks": 100},
    "p4": {"code": "P4", "subject": "General Engineering Science", "category": "Merit", "max_marks": 100},
    "p5": {"code": "P5", "subject": "Optional Subject I", "category": "Merit", "max_marks": 100},
    "p6": {"code": "P6", "subject": "Optional Subject II", "category": "Merit", "max_marks": 100},
}
QUALIFYING_PERCENT = 30.0
MARKS_CORRECT = 1.0
MARKS_WRONG = -1.0
MARKS_BONUS = 2.0
 
