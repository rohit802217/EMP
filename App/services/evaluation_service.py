"""
Generates the downloadable official marksheet image (PNG) for a
candidate, given their name, roll number, and paper-wise scores.
"""

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from config import PASS_MARK


def _load_fonts():
    try:
        return (
            ImageFont.truetype("arial.ttf", 32),
            ImageFont.truetype("arial.ttf", 20),
            ImageFont.truetype("arial.ttf", 16),
        )
    except IOError:
        default = ImageFont.load_default()
        return default, default, default


def generate_marksheet_img(student_name, roll_no, scores):
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    font_title, font_body, font_small = _load_fonts()

    draw.rectangle([10, 10, width - 10, height - 10], outline="black", width=3)
    draw.text((width // 2, 50), "OFFICIAL MARKSHEET", font=font_title, fill="black", anchor="mm")
    draw.line([(40, 90), (width - 40, 90)], fill="black", width=2)

    y = 130
    draw.text((60, y), f"Candidate Name: {student_name}", font=font_body, fill="black")
    y += 35
    draw.text((60, y), f"Roll Number: {roll_no}", font=font_body, fill="black")
    y += 50

    rows = [
        ("Paper", "Score", "Result"),
        ("P1 - English", f"{scores['p1']}/100", "Passed" if scores["p1"] >= PASS_MARK else "Failed"),
        ("P2 - Hindi", f"{scores['p2']}/100", "Passed" if scores["p2"] >= PASS_MARK else "Failed"),
        ("P3", f"{scores['p3']}/100", ""),
        ("P4", f"{scores['p4']}/100", ""),
        ("P5", f"{scores['p5']}/100", ""),
        ("P6", f"{scores['p6']}/100", ""),
    ]
    col_x = [60, 400, 580]

    for i, row in enumerate(rows):
        row_y = y + (i * 35)
        current_font = font_body if i == 0 else font_small
        for j, cell in enumerate(row):
            draw.text((col_x[j], row_y), str(cell), font=current_font, fill="black")

    y += (len(rows) * 35) + 20
    draw.line([(40, y), (width - 40, y)], fill="black", width=1)
    y += 20

    draw.text((60, y), f"Merit Score (P3-P6): {scores['merit_total']}/400", font=font_body, fill="black")
    y += 35
    draw.text((60, y), f"Percentage: {scores['merit_pct']:.2f}%", font=font_body, fill="black")
    y += 35
    draw.text((60, y), f"Overall Rank: #{scores.get('rank', 'N/A')}", font=font_body, fill="black")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
