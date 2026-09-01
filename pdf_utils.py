import logging
from pathlib import Path

import fitz  # PyMuPDF

logger = logging.getLogger("NYTCrossword")

# Extra margin (in points) kept around the detected content on each side.
CROP_PADDING = 6


def crop_whitespace(pdf_path: Path) -> None:
    """Trim excess whitespace margins from every page of a PDF in place.

    Some puzzle PDFs (notably the Sunday edition) are rendered with much
    larger blank margins than the daily puzzles. This detects the actual
    ink bounding box on each page and tightens the page's CropBox to it,
    leaving a small padding so nothing touches the edge.
    """
    doc = fitz.open(pdf_path)
    changed = False

    for page in doc:
        content_bbox = page.get_bbox() if hasattr(page, "get_bbox") else None
        if content_bbox is None:
            # Fall back to computing the bbox from drawings/text/images.
            content_bbox = _compute_content_bbox(page)

        if content_bbox is None or content_bbox.is_empty:
            continue

        padded = fitz.Rect(
            content_bbox.x0 - CROP_PADDING,
            content_bbox.y0 - CROP_PADDING,
            content_bbox.x1 + CROP_PADDING,
            content_bbox.y1 + CROP_PADDING,
        )
        padded &= page.rect  # clamp to the original page bounds

        if padded.is_empty or padded == page.rect:
            continue

        page.set_cropbox(padded)
        changed = True

    if changed:
        doc.saveIncr()
        logger.info("Trimmed whitespace margins: %s", pdf_path)
    else:
        logger.info("No whitespace trimming needed: %s", pdf_path)

    doc.close()


def _compute_content_bbox(page: "fitz.Page"):
    bbox = fitz.Rect()
    for block in page.get_text("blocks"):
        bbox |= fitz.Rect(block[:4])
    for drawing in page.get_drawings():
        bbox |= drawing["rect"]
    for image in page.get_image_info():
        bbox |= fitz.Rect(image["bbox"])
    return bbox if not bbox.is_empty else None
