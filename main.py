#!/usr/bin/env python3
"""
Price Label Printer - Pimaco A5Q-813
A5 landscape sheet | 13 columns x 14 rows = 182 labels per sheet
Input format: one label per line (e.g. R$25, R$100)

Usage:
    python main.py labels.txt
    python main.py labels.txt output.pdf
"""

import sys
import os
from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ─── A5Q-813 landscape sheet layout ──────────────────────────────────────────
PAGE_W, PAGE_H = landscape(A5)   # 595.28 x 419.53 pts  (210 x 148.5 mm)

COLUMNS        = 13
ROWS           = 14
LABELS_PER_SHEET = COLUMNS * ROWS   # 182

LABEL_W        = 13.0 * mm
LABEL_H        =  8.0 * mm

# Margins calibrated from reference PDF (real measurement)
MARGIN_LEFT    = 8.5 * mm
MARGIN_TOP     = 5.0 * mm

# Gap between labels calculated to fill the usable area
GAP_H = (PAGE_W - MARGIN_LEFT * 2 - COLUMNS * LABEL_W) / (COLUMNS - 1)
GAP_V = (PAGE_H - MARGIN_TOP  * 2 - ROWS    * LABEL_H) / (ROWS    - 1)

STEP_H = LABEL_W + GAP_H
STEP_V = LABEL_H + GAP_V

# ─── Font and automatic size by text length ───────────────────────────────────
FONT = "Times-Roman"

def font_size(text: str) -> float:
    n = len(text)
    if n <= 3:  return 14.5   # R$5
    if n == 4:  return 14.5   # R$25
    if n == 5:  return 11.5   # R$100
    return 5.5


def parse_lines(lines) -> list[str]:
    labels = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "x" in line:
            multiplier, _, text = line.partition("x")
            if multiplier.isdigit() and text:
                labels.extend([text] * int(multiplier))
                continue
        labels.append(line)
    return labels


def load_labels(txt_path: str) -> list[str]:
    if not os.path.exists(txt_path):
        print(f"[ERROR] File not found: {txt_path}")
        sys.exit(1)
    with open(txt_path, encoding="utf-8") as f:
        labels = parse_lines(f)
    print(f"[INFO] {len(labels)} label(s) loaded from '{txt_path}'")
    return labels


def generate_pdf(labels: list[str], dest) -> None:
    total_pages = max(1, -(-len(labels) // LABELS_PER_SHEET))

    c = canvas.Canvas(dest, pagesize=landscape(A5))

    idx = 0
    for _ in range(total_pages):
        for row in range(ROWS):
            for col in range(COLUMNS):
                if idx >= len(labels):
                    break

                text = labels[idx]
                idx += 1

                x = MARGIN_LEFT + col * STEP_H
                y = PAGE_H - MARGIN_TOP - (row + 1) * LABEL_H - row * GAP_V

                fs = font_size(text)
                c.setFont(FONT, fs)

                tw = c.stringWidth(text, FONT, fs)
                tx = x + (LABEL_W - tw) / 2
                ty = y + (LABEL_H - fs) / 2 + 0.5

                c.drawString(tx, ty, text)

            else:
                continue
            break

        c.showPage()

    c.save()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    txt_path = sys.argv[1]
    pdf_path = (
        sys.argv[2] if len(sys.argv) >= 3
        else txt_path.rsplit(".", 1)[0] + "_labels.pdf"
    )

    labels = load_labels(txt_path)
    generate_pdf(labels, pdf_path)


if __name__ == "__main__":
    main()
