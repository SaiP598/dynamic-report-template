"""Template-backed rendering: retain the supplied PDF's vector artwork and content.

The unchanged baseline is returned byte-for-byte. Customized output edits source
headings/decorations and, when reordered, composes complete section page fragments.
The private input PDF is never embedded into the Git repository.
"""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from ..data.defaults import DEFAULT_HEADINGS, SECTION_IDS, get_default_configuration

BODY_TOP = 132
BODY_BOTTOM = 707


class ReferenceReportError(ValueError):
    pass


def _anchors(document):
    found = {}
    for id_, title in zip(SECTION_IDS, DEFAULT_HEADINGS):
        for index, page in enumerate(document):
            matches = [r for r in page.search_for(title) if BODY_TOP <= r.y0 < BODY_BOTTOM]
            if matches:
                rect = matches[0]
                span = next(s for b in page.get_text("dict")["blocks"] for line in b.get("lines", [])
                            for s in line["spans"] if s["text"].strip() == title)
                found[id_] = (index, rect, span)
                break
        if id_ not in found:
            raise ReferenceReportError("The installed reference does not contain the expected report sections.")
    positions = [(found[id_][0], found[id_][1].y0) for id_ in SECTION_IDS]
    if positions != sorted(positions):
        raise ReferenceReportError("The installed reference has an unsupported section structure.")
    return found


def _font(document):
    for entry in document[0].get_fonts():
        if "Europa-Bold" in entry[3]:
            buffer = document.extract_font(entry[0])[3]
            if buffer:
                return buffer, fitz.Font(fontbuffer=buffer)
    return None, fitz.Font("helv")


def _edit_headings(document, configuration, anchors):
    buffer, font = _font(document)
    changes = {}
    reordered = [s["id"] for s in configuration["sections"]] != list(SECTION_IDS)
    for position, section in enumerate(configuration["sections"], 1):
        page_index, rect, span = anchors[section["id"]]
        if section["heading"] != span["text"].strip():
            changes.setdefault(page_index, []).append((rect, span, section["heading"]))
        if reordered and section["id"] not in ("legend", "patient-card"):
            page = document[page_index]
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for number in line["spans"]:
                        r = fitz.Rect(number["bbox"])
                        if r.x1 < 45 and abs(r.y0 - rect.y0) < 5 and number["text"].strip().isdigit():
                            changes.setdefault(page_index, []).append((r, number, str(position)))
    for index, replacements in changes.items():
        page = document[index]
        for rect, _, _ in replacements:
            page.add_redact_annot(rect, fill=None, cross_out=False)
        page.apply_redactions(images=0, graphics=0)
        for rect, span, text in replacements:
            numeric = rect.x1 < 45
            available = (rect.width + 2) if numeric else (589.5 - rect.x0)
            active_font = font if all(font.has_glyph(ord(c)) for c in text) else fitz.Font("helv")
            use_source = active_font is font and buffer is not None
            name = "ReferenceHeading" if use_source else "helv"
            if use_source:
                page.insert_font(fontname=name, fontbuffer=buffer)
            size = min(span["size"], span["size"] * available / max(active_font.text_length(text, fontsize=span["size"]), 1))
            color = fitz.sRGB_to_pdf(span["color"])
            page.insert_text(span["origin"], text, fontsize=size, fontname=name, color=color)


def _draw_formatted(pdf_canvas, formatting, top, height):
    text = formatting["text"]
    if not text:
        return
    size = formatting["fontSize"]
    font = "Helvetica" + ("-BoldOblique" if formatting["bold"] and formatting["italic"] else
                          "-Bold" if formatting["bold"] else "-Oblique" if formatting["italic"] else "")
    while True:
        style = ParagraphStyle("reference-decoration", fontName=font, fontSize=size,
                               leading=size * 1.2, alignment={"left": 0, "center": 1, "right": 2}[formatting["alignment"]],
                               textColor=formatting["color"])
        paragraph = Paragraph(escape(text).replace("\n", "<br/>"), style)
        _, used = paragraph.wrap(567, 10000)
        if used <= height:
            paragraph.drawOn(pdf_canvas, 22.5, 792 - top - used)
            return
        size *= .9


def _edit_decorations(document, configuration):
    baseline = get_default_configuration()
    header_changed = configuration["header"] != baseline["header"]
    footer_changed = configuration["footer"] != baseline["footer"]
    if not (header_changed or footer_changed):
        return
    for index, page in enumerate(document):
        if header_changed:
            page.add_redact_annot(fitz.Rect(20, 20, 592, 124), fill=(1, 1, 1), cross_out=False)
        if footer_changed:
            page.add_redact_annot(fitz.Rect(20, 709, 592, 765), fill=(1, 1, 1), cross_out=False)
        page.apply_redactions(images=0, graphics=0)
        if not ((header_changed and configuration["header"]["text"]) or
                (footer_changed and configuration["footer"]["text"])):
            continue
        stream = BytesIO()
        overlay = canvas.Canvas(stream, pagesize=(612, 792))
        if header_changed:
            _draw_formatted(overlay, configuration["header"], 23, 98)
        if footer_changed:
            _draw_formatted(overlay, configuration["footer"], 713, 49)
        overlay.save()
        with fitz.open(stream=stream.getvalue(), filetype="pdf") as overlay_pdf:
            page.show_pdf_page(page.rect, overlay_pdf, 0)


def render_reference_report(configuration, path):
    path = Path(path)
    if not path.is_file():
        raise ReferenceReportError("The reference PDF is unavailable. Install the assessment attachment and retry.")
    original = path.read_bytes()
    try:
        document = fitz.open(stream=original, filetype="pdf")
    except (RuntimeError, ValueError) as error:
        raise ReferenceReportError("The reference PDF could not be opened.") from error
    with document:
        if document.is_encrypted or len(document) != 45 or any(p.rect != fitz.Rect(0, 0, 612, 792) for p in document):
            raise ReferenceReportError("Install the original 45-page US Letter assessment PDF.")
        anchors = _anchors(document)
        if configuration == get_default_configuration():
            return original
        _edit_headings(document, configuration, anchors)
        reordered = [s["id"] for s in configuration["sections"]] != list(SECTION_IDS)
        if not reordered:
            _edit_decorations(document, configuration)
            return document.tobytes(garbage=4, deflate=True)
        # Edit the original pages before importing clipped forms. Redacting an
        # imported full-page form can otherwise remove unrelated logos or content.
        _edit_decorations(document, configuration)
        for source in document:
            source.add_redact_annot(fitz.Rect(535, 765, 592, 780), fill=(1, 1, 1), cross_out=False)
            source.apply_redactions(images=0, graphics=0)
        with fitz.open() as result:
            for section in configuration["sections"]:
                position = SECTION_IDS.index(section["id"])
                start_page, start_rect, _ = anchors[section["id"]]
                stop = anchors[SECTION_IDS[position + 1]] if position + 1 < len(SECTION_IDS) else None
                end_page = (stop[0] if stop[0] == start_page else stop[0] - 1) if stop else len(document) - 1
                for source_page in range(start_page, end_page + 1):
                    top = max(BODY_TOP, start_rect.y0 - 8) if source_page == start_page else BODY_TOP
                    bottom = min(BODY_BOTTOM, stop[1].y0 - 8) if stop and source_page == stop[0] else BODY_BOTTOM
                    if bottom <= top:
                        continue
                    output = result.new_page(width=612, height=792)
                    # Original fonts, logos, colors, rules, tables, and clinical text remain vector content.
                    output.show_pdf_page(fitz.Rect(0, 0, 612, BODY_TOP), document, source_page,
                                         clip=fitz.Rect(0, 0, 612, BODY_TOP))
                    output.show_pdf_page(fitz.Rect(0, BODY_TOP, 612, BODY_TOP + bottom - top), document, source_page,
                                         clip=fitz.Rect(0, top, 612, bottom))
                    output.show_pdf_page(fitz.Rect(0, BODY_BOTTOM, 612, 792), document, source_page,
                                         clip=fitz.Rect(0, BODY_BOTTOM, 612, 792))
            for index, page in enumerate(result):
                page.insert_text((535, 771), f"Page {index + 1} of {len(result)}", fontname="helv", fontsize=6)

            return result.tobytes(garbage=4, deflate=True)
