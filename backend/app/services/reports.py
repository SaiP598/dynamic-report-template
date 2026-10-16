"""Paginated synthetic report rendering, independent of browser drafts."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, LongTable, TableStyle, Flowable

from ..data.report_content import get_report_content

_FONT_DIR = Path(reportlab.__file__).parent / "fonts"
for name, filename in [("Report", "Vera.ttf"), ("ReportBold", "VeraBd.ttf"),
                       ("ReportItalic", "VeraIt.ttf"), ("ReportBoldItalic", "VeraBI.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(_FONT_DIR / filename)))

_BODY = ParagraphStyle("body", fontName="Report", fontSize=7.5, leading=10.5, spaceAfter=6)
_HEADING = ParagraphStyle("heading", parent=_BODY, fontName="ReportBold", fontSize=11,
                          leading=15, textColor=colors.HexColor("#008577"), spaceBefore=15,
                          spaceAfter=9, keepWithNext=True)
_LABEL = ParagraphStyle("label", parent=_BODY, fontName="ReportBold", keepWithNext=True)


def paragraph(value, style=_BODY):
    # Free text must never be interpreted as ReportLab's XML markup.
    return Paragraph(escape(str(value)).replace("\n", "<br/>"), style)


def formatted_text(formatting, width, max_height=110):
    name = "Report" + ("Bold" if formatting["bold"] else "") + ("Italic" if formatting["italic"] else "")
    size = formatting["fontSize"]
    while True:
        style = ParagraphStyle("decoration", fontName=name, fontSize=size, leading=size * 1.25,
                               alignment={"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}[formatting["alignment"]],
                               textColor=colors.HexColor(formatting["color"]))
        block = paragraph(formatting["text"], style)
        height = block.wrap(width, 1000)[1] if formatting["text"] else 0
        if height <= max_height:
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


class SectionHeading(Flowable):
    keepWithNext = True
    spaceBefore = 15
    spaceAfter = 9

    def __init__(self, index, heading):
        super().__init__()
        self.index = index
        self.paragraph = paragraph(heading, ParagraphStyle("section-heading", parent=_HEADING, leftIndent=25))

    def wrap(self, available_width, available_height):
        self.width, self.height = self.paragraph.wrap(available_width, available_height)
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(colors.HexColor("#e8f6f3"))
        self.canv.circle(10, self.height - 6, 9, fill=1, stroke=0)
        self.canv.setFillColor(colors.HexColor("#009688"))
        self.canv.setFont("ReportBold", 9)
        self.canv.drawCentredString(10, self.height - 9, str(self.index))
        self.canv.restoreState()
        self.paragraph.drawOn(self.canv, 0, 0)


def render_report(configuration, content=None):
    content = content if content is not None else get_report_content()
    output = BytesIO()
    width = letter[0] - 45
    header, header_height = formatted_text(configuration["header"], width - 12, 85)
    footer, footer_height = formatted_text(configuration["footer"], 195, 49)
    band_height = max(28, header_height + 8)
    top = 135 + band_height + 12
    bottom = 90
    document = SimpleDocTemplate(output, pagesize=letter, leftMargin=22.5, rightMargin=22.5,
                                 topMargin=top, bottomMargin=bottom, title="Report template - synthetic demonstration",
                                 author="Dynamic Report Template")

    def decorate(canvas, doc):
        canvas.saveState()
        teal = colors.HexColor("#009688")
        canvas.setFillColor(colors.HexColor("#20332f"))
        canvas.setFont("Report", 22)
        canvas.drawString(22.5, 735, "DEMO")
        canvas.setFont("Report", 8)
        canvas.drawString(24, 720, "G E N O M I C S")
        canvas.setFont("ReportBold", 6)
        canvas.drawString(22.5, 690, "Demo Laboratory")
        canvas.setFont("Report", 6)
        canvas.drawString(22.5, 678, "Synthetic data - not for clinical use")
        columns = [(215, 125, "PATIENT INFORMATION", [
            ("NAME", content["patient"]["name"]), ("DOB", content["patient"]["dateOfBirth"]),
            ("SEX", content["patient"]["sex"])]),
            (340, 125, "SPECIMEN DETAILS", [("SAMPLE ID", content["specimen"]["sampleId"]),
             ("TYPE", content["specimen"]["type"]), ("REPORT DATE", content["specimen"]["reportDate"])]),
            (465, 125, "PROVIDER INFORMATION", [("PROVIDER", content["provider"]["name"]),
             ("FACILITY", content["provider"]["facility"])])]
        for x, column_width, title, rows in columns:
            canvas.setFillColor(teal)
            canvas.rect(x, 753, column_width, 17, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont("Report", 5.2)
            canvas.drawString(x + 4, 760, title)
            for row_index, (label, value) in enumerate(rows):
                line = paragraph(f"{label}: {value}", ParagraphStyle("metadata", parent=_BODY, fontSize=5.5, leading=7))
                _, height = line.wrap(column_width - 8, 50)
                line.drawOn(canvas, x + 3, 744 - row_index * 16 - height)
        # Reference-inspired title strip, with editable plain text.
        canvas.setFillColor(teal)
        canvas.rect(22.5, 792 - 135 - band_height, width, band_height, fill=1, stroke=0)
        if header_height:
            header.drawOn(canvas, 28.5, 792 - 135 - (band_height + header_height) / 2)
        canvas.setStrokeColor(colors.HexColor("#d6dfda"))
        canvas.line(22.5, 82, 589.5, 82)
        canvas.setFillColor(teal)
        canvas.setFont("ReportBold", 9)
        canvas.drawString(22.5, 65, "DEMO LAB")
        canvas.setFont("Report", 5)
        canvas.drawString(22.5, 57, "LABORATORY")
        if footer_height:
            footer.drawOn(canvas, 105, 75 - footer_height)
        canvas.setFillColor(teal)
        canvas.setFont("ReportBold", 8)
        canvas.drawString(317, 65, "PARTNER")
        canvas.setFont("Report", 5)
        canvas.drawString(317, 57, "LABORATORY")
        right_footer = paragraph("Laboratory Performing Test\nDemo Laboratory\n"
                                 "Laboratory Director: [Name]\n[Address]\n[Phone] | [Certification]",
                                 ParagraphStyle("lab-footer", parent=_BODY, fontSize=5.5, leading=8))
        _, height = right_footer.wrap(201, 60)
        right_footer.drawOn(canvas, 388.5, 75 - height)
        canvas.setFont("Report", 6)
        canvas.setFillColor(colors.HexColor("#596b66"))
        canvas.drawRightString(589.5, 20, f"Page {doc.page}")
        canvas.restoreState()

    story = [paragraph("SYNTHETIC DEMONSTRATION - NOT FOR CLINICAL USE", _LABEL)]
    for index, section in enumerate(configuration["sections"], 1):
        block = content["sections"][section["id"]]
        story.append(SectionHeading(index, section["heading"]))
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
