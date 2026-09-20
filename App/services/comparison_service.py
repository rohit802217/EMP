"""
Parsing OCR'd answer-sheet text into {question_number: answer}
dicts, and converting those to/from the editable DataFrames used
in the Compare Answer Sheet page.
"""

import re
import pandas as pd

from utils.validators import clean_answer

_SAME_LINE_PATTERN = re.compile(
    r"""
    ^\s*
    (?:question\s*|q\.?\s*)?
    (\d{1,3})
    \s*
    (?:[.):\-]|->)?
    \s*
    (?:\(\s*)?
    (A|B|C|D|DELETED)
    \s*
    (?:\))?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_QUESTION_ONLY_PATTERN = re.compile(
    r"""
    ^\s*
    (?:question\s*|q\.?\s*)?
    (\d{1,3})
    \s*
    (?:[.):\-])?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_ANSWER_ONLY_PATTERN = re.compile(
    r"""
    ^\s*
    \(?\s*
    (A|B|C|D|DELETED)
    \s*\)?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


def parse_answers(raw_text):
    """
    Parse Question -> Answer pairs out of OCR'd text.
    Handles same-line ('Q1 B') and split-across-two-lines
    ('Q1' then 'B' on the next line) formats.
    """
    if not raw_text:
        return {}

    text = (
        raw_text.replace("—", "-").replace("–", "-").replace("−", "-")
        .replace("：", ":").replace("（", "(").replace("）", ")")
    )

    lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if line.strip()
    ]

    answers = {}
    i = 0
    while i < len(lines):
        line = lines[i]

        match = _SAME_LINE_PATTERN.match(line)
        if match:
            q_num = int(match.group(1))
            answers[q_num] = match.group(2).upper()
            i += 1
            continue

        q_match = _QUESTION_ONLY_PATTERN.match(line)
        if q_match and i + 1 < len(lines):
            next_line = lines[i + 1]
            ans_match = _ANSWER_ONLY_PATTERN.match(next_line)
            if ans_match:
                answers[int(q_match.group(1))] = ans_match.group(1).upper()
                i += 2
                continue

        i += 1

    return dict(sorted(answers.items()))


def answers_dict_to_df(answers_dict, value_col_name):
    """Convert a {question: answer} dict into a 2-column DataFrame."""
    if not answers_dict:
        return pd.DataFrame(columns=["Question", value_col_name])

    return pd.DataFrame(sorted(answers_dict.items()), columns=["Question", value_col_name])


def dataframe_to_answer_map(df, answer_column):
    """Convert an (edited) answers DataFrame back into a {question: answer} dict."""
    answer_map = {}

    if df is None or df.empty:
        return answer_map

    for _, row in df.iterrows():
        question = row.get("Question")
        if pd.isna(question):
            continue

        try:
            q_num = int(float(question))
        except (ValueError, TypeError):
            continue

        answer = clean_answer(row.get(answer_column, ""))
        if answer:
            answer_map[q_num] = answer

    return answer_map
