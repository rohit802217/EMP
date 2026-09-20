"""
Everything related to the persistent candidate leaderboard:
loading/saving, rank calculation, bulk import from CSV/Excel,
and updating a candidate's record from an answer-sheet comparison.
"""

import streamlit as st
import pandas as pd
import json

from config import DATA_FILE, MAX_MERIT_TOTAL
from utils.file_utils import read_json_list, write_json_list
from utils.validators import is_valid_roll_no, clamp_merit_score


# ------------------------------------------------------------------
# Load / Save
# ------------------------------------------------------------------

def load_data():
    return read_json_list(DATA_FILE)


def save_data(db):
    write_json_list(DATA_FILE, db)


# ------------------------------------------------------------------
# Rank calculation
# ------------------------------------------------------------------

def recalculate_ranks(db):
    """Competition ranks within a reviewed exam/scheme cohort; ties share rank."""
    db.sort(key=lambda x: float(x.get("merit_total", 0)), reverse=True)
    groups = {}
    for record in db:
        record['rank'] = None
        record['ranked_candidates'] = 0
        if not isinstance(record.get("scores"), dict):
            record["scores"] = {}
        record['scores']['rank'] = None
        papers = record.get('papers', {})
        if (record.get('reviewed_complete') is not True or
                record.get('qualifying_pass') is not True or
                set(papers) != {f'p{i}' for i in range(1,7)} or
                not record.get('exam_id') or not record.get('marking_scheme')):
            continue
        cohort = json.dumps([record['exam_id'].strip().casefold(),record['marking_scheme'],
                             {p:r['max_score'] for p,r in papers.items()}],sort_keys=True)
        groups.setdefault(cohort,[]).append(record)
    for records in groups.values():
        previous = None
        rank = 0
        for position, record in enumerate(records,1):
            score = float(record['merit_total'])
            if score != previous:
                rank = position
            previous = score
            record['rank'] = record['scores']['rank'] = rank
            record['ranked_candidates'] = len(records)
    return db


def _find_candidate(db, roll_no):
    for record in db:
        if str(record.get("roll_no", "")).strip() == roll_no:
            return record
    return None


# ------------------------------------------------------------------
# Update / create a candidate from an answer-sheet comparison
# ------------------------------------------------------------------

def update_leaderboard_from_comparison(
    roll_no,
    final_score,
    correct_count,
    incorrect_count,
    unanswered_count,
    deleted_count,
    accuracy,
    student_name="",
):
    """
    Create or update a candidate's leaderboard entry from a
    Compare Answer Sheet result, then recalculate all ranks.

    Returns (success: bool, result: dict | error_message: str)
    """
    roll_no = str(roll_no).strip()
    student_name = str(student_name).strip()

    if not is_valid_roll_no(roll_no):
        return False, "Candidate Roll Number is required."

    db = load_data()

    final_score = clamp_merit_score(final_score)
    percentage = round((final_score / MAX_MERIT_TOTAL) * 100, 2)

    comparison_data = {
        "correct": int(correct_count),
        "incorrect": int(incorrect_count),
        "unanswered": int(unanswered_count),
        "deleted": int(deleted_count),
        "accuracy": round(float(accuracy), 2),
        "final_score": final_score,
    }

    candidate = _find_candidate(db, roll_no)

    if candidate is not None:
        candidate["merit_total"] = final_score
        candidate["pct"] = percentage

        # Only overwrite the name if a real one was provided this time,
        # so we don't clobber an existing name with a blank field.
        if student_name:
            candidate["name"] = student_name

        if not isinstance(candidate.get("scores"), dict):
            candidate["scores"] = {}
        candidate["scores"]["merit_total"] = final_score
        candidate["scores"]["merit_pct"] = percentage

        candidate["comparison"] = comparison_data
        candidate['reviewed_complete'] = False
        action = "updated"
    else:
        candidate = {
            "name": student_name if student_name else f"Candidate {roll_no}",
            "roll_no": roll_no,
            "merit_total": final_score,
            "pct": percentage,
            "scores": {
                "p1": 0, "p2": 0,
                "p3": 0, "p4": 0, "p5": 0, "p6": 0,
                "merit_total": final_score,
                "merit_pct": percentage,
            },
            "comparison": comparison_data,
        }
        db.append(candidate)
        action = "created"

    db = recalculate_ranks(db)
    updated_candidate = _find_candidate(db, roll_no)
    save_data(db)

    if updated_candidate is None:
        return False, "Candidate could not be saved."

    return True, {
        "candidate": updated_candidate,
        "action": action,
        "total_candidates": len(db),
    }


# ------------------------------------------------------------------
# Bulk import from CSV / Excel
# ------------------------------------------------------------------

_RENAME_MAP = {
    "candidate_name": "name",
    "student_name": "name",
    "candidate": "name",
    "roll_number": "roll_no",
    "roll": "roll_no",
    "rollnumber": "roll_no",
    "merit_score": "merit_total",
    "merit_marks": "merit_total",
    "merit": "merit_total",
    "total": "merit_total",
    "percentage": "pct",
    "percent": "pct",
}

_REQUIRED_COLUMNS = ["name", "roll_no", "merit_total"]


def import_leaderboard_file(uploaded_file):
    """
    Parse an uploaded CSV/Excel file into a list of leaderboard
    record dicts. Reports errors via st.error and returns None
    on failure so the UI layer can just check for None.
    """
    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel.")
            return None
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        return None

    df.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]
    df = df.rename(columns=_RENAME_MAP)

    missing = [col for col in _REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        st.error(
            "Missing required columns: " + ", ".join(missing) +
            "\n\nRequired columns:\nname, roll_no, merit_total"
        )
        return None

    df["name"] = df["name"].fillna("").astype(str).str.strip()
    df["roll_no"] = df["roll_no"].fillna("").astype(str).str.strip()
    df["merit_total"] = pd.to_numeric(df["merit_total"], errors="coerce")

    df = df[
        (df["name"] != "") & (df["roll_no"] != "") & (df["merit_total"].notna())
    ].copy()
    df["merit_total"] = df["merit_total"].clip(lower=0, upper=MAX_MERIT_TOTAL)

    if "pct" not in df.columns:
        df["pct"] = (df["merit_total"] / MAX_MERIT_TOTAL) * 100
    else:
        df["pct"] = pd.to_numeric(df["pct"], errors="coerce")
        df["pct"] = df["pct"].fillna((df["merit_total"] / MAX_MERIT_TOTAL) * 100)

    records = []
    for _, row in df.iterrows():
        def get_score(column):
            if column not in df.columns:
                return 0
            value = pd.to_numeric(row[column], errors="coerce")
            return 0 if pd.isna(value) else int(value)

        scores = {
            "p1": get_score("p1"), "p2": get_score("p2"),
            "p3": get_score("p3"), "p4": get_score("p4"),
            "p5": get_score("p5"), "p6": get_score("p6"),
            "merit_total": float(row["merit_total"]),
            "merit_pct": float(row["pct"]),
        }

        records.append({
            "reviewed_complete": False,
            "name": row["name"],
            "roll_no": row["roll_no"],
            "merit_total": float(row["merit_total"]),
            "pct": float(row["pct"]),
            "scores": scores,
        })

    return records
