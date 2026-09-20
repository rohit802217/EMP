"""
Generic file I/O helpers.

These are deliberately generic (not tied to leaderboard or vacancy
data) so any service can reuse them for reading/writing a JSON list.
"""

import json
import os
import tempfile


def read_json_list(file_path):
    """
    Read a JSON file that is expected to contain a list.
    Returns an empty list if the file doesn't exist or is invalid,
    so callers never have to special-case a missing file.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def write_json_list(file_path, data):
    """
    Write a list to a JSON file atomically: write to a temp file first,
    then swap it in with os.replace(). This guarantees the real file is
    never left half-written or corrupted if the app crashes, loses power,
    or is killed mid-save.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    dir_name = os.path.dirname(file_path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, file_path)  # atomic on both Windows and Linux
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
