"""Paginated synthetic report rendering, independent of browser drafts."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, LongTable, TableStyle

from ..data.report_content import get_report_content

_FONT_DIR = Path(reportlab.__file__).parent / "fonts"
for name, filename in [("Report", "Vera.ttf"), ("ReportBold", "VeraBd.ttf"),
                       ("ReportItalic", "VeraIt.ttf"), ("ReportBoldItalic", "VeraBI.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(_FONT_DIR / filename)))

_BODY = ParagraphStyle("body", fontName="Report", fontSize=9, leading=13, spaceAfter=7)
_HEADING = ParagraphStyle("heading", parent=_BODY, fontName="ReportBold", fontSize=14,
                          leading=19, textColor=colors.HexColor("#008577"), spaceBefore=15,
                          spaceAfter=9, keepWithNext=True)
_LABEL = ParagraphStyle("label", parent=_BODY, fontName="ReportBold", keepWithNext=True)


def paragraph(value, style=_BODY):
    # Free text must never be interpreted as ReportLab's XML markup.
    return Paragraph(escape(str(value)).replace("\n", "<br/>"), style)


def formatted_text(formatting, width):
    name = "Report" + ("Bold" if formatting["bold"] else "") + ("Italic" if formatting["italic"] else "")
    size = formatting["fontSize"]
    while True:
        style = ParagraphStyle("decoration", fontName=name, fontSize=size, leading=size * 1.25,
                               alignment={"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}[formatting["alignment"]],
                               textColor=colors.HexColor(formatting["color"]))
        block = paragraph(formatting["text"], style)
        height = block.wrap(width, 1000)[1] if formatting["text"] else 0
        if height <= 110:
            return block, height
        size = size - 1 if size > 6 else size * .9


def make_table(columns, rows, widths, risk_colors=False):
    cells = [[paragraph(c, _LABEL) for c in columns]]
    cells.extend([[paragraph(c) for c in row] for row in rows])
    table = LongTable(cells, colWidths=widths, repeatRows=1, hAlign="LEFT",
                      splitByRow=1, splitInRow=1)
    commands = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4f1")),
                ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#d6dfda")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
    if risk_colors:
        for col, color in [(2, "#d4eadb"), (3, "#f6e7d7"), (4, "#f3d8dc")]:
            commands.append(("BACKGROUND", (col, 1), (col, -1), colors.HexColor(color)))
    table.setStyle(TableStyle(commands))
    return table


def render_report(configuration, content=None):
    content = content if content is not None else get_report_content()
    output = BytesIO()
    width = A4[0] - 72
    header, header_height = formatted_text(configuration["header"], width)
    footer, footer_height = formatted_text(configuration["footer"], width)
    top = header_height + 94
    bottom = footer_height + 48
    document = SimpleDocTemplate(output, pagesize=A4, leftMargin=36, rightMargin=36,
                                 topMargin=top, bottomMargin=bottom, title="Dynamic report - synthetic demonstration",
                                 author="Dynamic Report Template")

    def decorate(canvas, doc):
        canvas.saveState()
        if header_height:
            header.drawOn(canvas, 36, A4[1] - 25 - header_height)
        metadata = (f"Patient: {content['patient']['name']} | Sample: {content['specimen']['sampleId']}\n"
                    f"Provider: {content['provider']['name']} | Report date: {content['specimen']['reportDate']}")
        block = paragraph(metadata, ParagraphStyle("metadata", parent=_BODY, fontSize=8, leading=11))
        _, height = block.wrap(width, 100)
        block.drawOn(canvas, 36, A4[1] - 39 - header_height - height)
        canvas.setStrokeColor(colors.HexColor("#d6dfda"))
        canvas.line(36, A4[1] - top + 10, A4[0] - 36, A4[1] - top + 10)
        if footer_height:
            footer.drawOn(canvas, 36, 32)
        canvas.setFont("Report", 7)
        canvas.setFillColor(colors.HexColor("#596b66"))
        canvas.drawRightString(A4[0] - 36, 17, f"Page {doc.page}")
        canvas.restoreState()

    story = [paragraph("SYNTHETIC DEMONSTRATION - NOT FOR CLINICAL USE", _LABEL)]
    for index, section in enumerate(configuration["sections"], 1):
        block = content["sections"][section["id"]]
        story.append(paragraph(f"{index}. {section['heading']}", _HEADING))
        for text in block.get("paragraphs", []):
            story.append(paragraph(text))
        id_ = section["id"]
        if id_ == "current-medications":
            for label, key in [("Current medications", "medications"), ("Unrecognized medications", "unrecognized"),
                               ("Outside scope", "outsideScope")]:
                story.append(paragraph(f"{label}: {', '.join(block[key]) or 'None'}"))
        elif id_ == "risk-management":
            for item in block["items"]:
                story.extend([paragraph(item["title"], _LABEL), paragraph(item["summary"]), paragraph(item["details"])])
        elif id_ == "impacted-medications":
            rows = [[r["category"], r["drugClass"], *["\n".join(r[k]) for k in ("standard", "caution", "alternatives")]] for r in block["rows"]]
            story.append(make_table(block["columns"], rows, [width * n for n in (.16, .18, .22, .22, .22)], True))
        elif id_ == "dosing-guidance":
            for item in block["items"]:
                story.extend([paragraph(f"{item['medication']} | Evidence: {item['evidence']}", _LABEL),
                              paragraph(item["finding"]), paragraph(item["guidance"])])
        elif id_ == "legend":
            for item in block["items"]:
                story.append(paragraph(item["label"]))
            story.append(paragraph("Evidence strength: " + ", ".join(block["evidenceLevels"])))
        elif id_ in ("test-details", "patient-card"):
            rows = [[r[k] for k in ("gene", "genotype", "phenotype")] for r in block["rows"]]
            story.append(make_table(["Gene", "Genotype", "Phenotype"], rows, [width / 3] * 3))
        story.append(Spacer(1, 8))
    document.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return output.getvalue()
