"""Export helpers for PDF generation."""
from __future__ import annotations

import io
import textwrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def text_to_pdf_bytes(title: str, body: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin_x = 48
    y = height - 56

    c.setTitle(title)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, title)
    y -= 24

    c.setFont("Helvetica", 10)
    wrap_width = 100

    for paragraph in body.splitlines():
        text = paragraph.strip()
        lines = [""] if text == "" else textwrap.wrap(text, width=wrap_width)
        for line in lines:
            if y < 56:
                c.showPage()
                y = height - 56
                c.setFont("Helvetica", 10)
            c.drawString(margin_x, y, line)
            y -= 14

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
