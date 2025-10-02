from __future__ import annotations
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import plotly.graph_objects as go
import tempfile, os

def _save_fig_png(fig: go.Figure) -> str:
    # Requires kaleido installed
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    tmp.close()
    fig.write_image(tmp.name, scale=2)
    return tmp.name

def export_board_pack(pdf_path: str, title: str, blocks: list[tuple[str, go.Figure]]):
    c = canvas.Canvas(pdf_path, pagesize=LETTER)
    width, height = LETTER
    margin = 0.75*inch

    for page_title, fig in blocks:
        c.setFont('Helvetica-Bold', 16)
        c.drawString(margin, height - margin, title)
        c.setFont('Helvetica', 12)
        c.drawString(margin, height - margin - 18, page_title)

        img_path = _save_fig_png(fig)
        try:
            # Fit image into area
            img_w, img_h = 7.0*inch, 4.2*inch
            c.drawImage(img_path, margin, height - margin - 18 - img_h - 12, width=img_w, height=img_h, preserveAspectRatio=True, anchor='nw')
        finally:
            try: os.remove(img_path)
            except: pass

        c.showPage()

    c.save()
    return pdf_path
