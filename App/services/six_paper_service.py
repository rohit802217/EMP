"""Six-paper upload parsing, evaluation and leaderboard persistence."""

import csv
import json
import re
from io import StringIO

from config import (
    PAPERS, QUALIFYING_PERCENT, MARKS_CORRECT, MARKS_WRONG, MARKS_BONUS,
    MAX_MERIT_TOTAL,
)
from services.comparison_service import parse_answers
from services.ocr_service import extract_text_from_file
from services.leaderboard_service import load_data, save_data, recalculate_ranks
from utils.validators import clean_answer


def _file_bytes(uploaded_file):
    uploaded_file.seek(0)
    data = uploaded_file.read()
    uploaded_file.seek(0)
    return data


def parse_uploaded_answers(uploaded_file):
    """Return a normalized {question_number: answer} map from CSV/JSON/image/PDF."""
    if uploaded_file is None:
        return {}
    name = uploaded_file.name.lower()
    raw = _file_bytes(uploaded_file)
    answers = {}

    if name.endswith(".json"):
        payload = json.loads(raw.decode("utf-8-sig"))
        if isinstance(payload, dict):
            source = payload.get("answers", payload)
            for q, answer in source.items():
                if str(q).strip().isdigit():
                    value = clean_answer(answer)
                    if value in {"A", "B", "C", "D", "DELETED", "BLANK", "*"}:
                        answers[int(q)] = value
        elif isinstance(payload, list):
            for row in payload:
                if isinstance(row, dict):
                    q = row.get("question", row.get("q", row.get("number")))
                    a = row.get("answer", row.get("option", row.get("response")))
                    if str(q).strip().isdigit() and clean_answer(a):
                        answers[int(q)] = clean_answer(a)
        return dict(sorted(answers.items()))

    if name.endswith(".csv"):
        text = raw.decode("utf-8-sig", errors="replace")
        rows = list(csv.reader(StringIO(text)))
        for row in rows:
            if len(row) < 2:
                continue
            q = re.sub(r"\D", "", str(row[0]))
            answer = clean_answer(row[1])
            if q and answer in {"A", "B", "C", "D", "DELETED", "BLANK", "*"}:
                answers[int(q)] = answer
        if answers:
            return dict(sorted(answers.items()))
        return parse_answers(text)

    uploaded_file.seek(0)
    return parse_answers(extract_text_from_file(uploaded_file))


def parse_deleted_questions(text):
    return {int(x) for x in re.findall(r"\d+", text or "") if int(x) > 0}


def evaluate_paper(candidate_answers, key_answers, deleted_questions, correct_marks=MARKS_CORRECT, wrong_penalty=-MARKS_WRONG, bonus_marks=MARKS_BONUS):
    if any(v not in ('A','B','C','D','DELETED') for v in key_answers.values()):
        raise ValueError('Unresolved key cells: review required.')
    if not key_answers or not candidate_answers:
        raise ValueError('Extraction incomplete: review required.')
    if any(v not in ('A','B','C','D','*','BLANK') for v in candidate_answers.values()):
        raise ValueError('Unresolved response cells: review required.')
    deleted = set(deleted_questions) | {q for q,a in key_answers.items() if a == 'DELETED'}
    if not deleted <= set(key_answers):
        raise ValueError('Deleted question numbers must exist in the key.')
    if set(candidate_answers) != set(key_answers):
        raise ValueError('Response and key question numbers must match; explicitly mark unanswered questions BLANK.')
    questions = sorted(set(key_answers) - deleted)
    correct = wrong = unanswered = 0
    details = []
    for q in questions:
        expected = key_answers.get(q)
        actual = candidate_answers.get(q)
        if expected not in {"A", "B", "C", "D"}:
            continue
        if actual in (None, 'BLANK'):
            status = "Unanswered"
            unanswered += 1
        elif actual == expected:
            status = "Correct"
            correct += 1
        else:
            status = "Wrong"
            wrong += 1
        details.append({"Question": q, "Response": actual or "—", "Key": expected, "Result": status})

    bonus = len(deleted)
    score = correct * correct_marks - wrong * wrong_penalty + bonus * bonus_marks
    max_score = len(questions) * correct_marks + bonus * bonus_marks
    score = max(0.0, min(float(max_score), float(score)))
    percentage = (score / max_score * 100.0) if max_score else 0.0
    return {
        "correct": correct, "wrong": wrong, "unanswered": unanswered,
        "bonus": bonus, "score": round(score, 2), "max_score": round(max_score, 2),
        "percentage": round(percentage, 2), "details": details,
    }


def build_candidate(name, roll_no, paper_results):
    qualifying_pass = all(paper_results[p]["percentage"] >= QUALIFYING_PERCENT for p in ("p1", "p2"))
    merit_total = round(sum(paper_results[p]["score"] for p in ("p3", "p4", "p5", "p6")), 2)
    merit_max = round(sum(paper_results[p]["max_score"] for p in ("p3", "p4", "p5", "p6")), 2)
    merit_pct = round((merit_total / merit_max * 100.0), 2) if merit_max else 0.0
    ranking_score = merit_total if qualifying_pass else 0.0
    scores = {p: paper_results[p]["score"] for p in PAPERS}
    scores.update({"merit_total": merit_total, "merit_pct": merit_pct})
    return {
        "name": name.strip(), "roll_no": roll_no.strip(),
        "status": "Qualified" if qualifying_pass else "Disqualified",
        "qualifying_pass": qualifying_pass,
        "merit_total": ranking_score, "raw_merit_total": merit_total,
        "merit_max": merit_max or MAX_MERIT_TOTAL,
        "pct": merit_pct if qualifying_pass else 0.0,
        "scores": scores, "papers": paper_results,
    }


def save_candidate(candidate):
    db = load_data()
    roll = candidate["roll_no"]
    db = [r for r in db if str(r.get("roll_no", "")).strip() != roll]
    db.append(candidate)
    db = recalculate_ranks(db)
    save_data(db)
    return next(r for r in db if str(r.get("roll_no", "")).strip() == roll), len(db)
