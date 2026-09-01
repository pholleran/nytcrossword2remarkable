from pathlib import Path

import fitz

from pdf_utils import crop_whitespace


def _make_pdf_with_margins(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    # Draw a small rectangle of "content" far from the page edges, leaving
    # large blank margins on every side, similar to the Sunday puzzle PDFs.
    page.draw_rect(fitz.Rect(200, 300, 400, 500), color=(0, 0, 0), fill=(0, 0, 0))
    doc.save(path)
    doc.close()


def test_crop_whitespace_tightens_cropbox_around_content(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _make_pdf_with_margins(pdf_path)

    doc = fitz.open(pdf_path)
    original_cropbox = doc[0].cropbox
    doc.close()

    crop_whitespace(pdf_path)

    doc = fitz.open(pdf_path)
    cropped = doc[0].cropbox
    doc.close()

    assert cropped.width < original_cropbox.width
    assert cropped.height < original_cropbox.height
    # Content rectangle plus padding should still be fully contained.
    assert cropped.x0 <= 200 and cropped.x1 >= 400
    assert cropped.y0 <= 300 and cropped.y1 >= 500


def test_crop_whitespace_is_noop_for_full_bleed_content(tmp_path):
    pdf_path = tmp_path / "full_bleed.pdf"
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    page.draw_rect(page.rect, color=(0, 0, 0), fill=(0, 0, 0))
    doc.save(pdf_path)
    doc.close()

    crop_whitespace(pdf_path)

    doc = fitz.open(pdf_path)
    cropbox = doc[0].cropbox
    mediabox = doc[0].mediabox
    doc.close()

    assert cropbox == mediabox
