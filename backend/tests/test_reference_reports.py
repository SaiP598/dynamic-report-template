"""Nonclinical generated fixture exercises the original-PDF rendering path."""
from unittest.mock import patch
import pymupdf as fitz
import pytest
from app import create_app
from app.data.defaults import DEFAULT_HEADINGS, get_default_configuration
from app.services.reference_reports import ReferenceReportError, render_reference_report


@pytest.fixture
def reference(tmp_path):
    path = tmp_path / "reference.pdf"
    locations = [(0, 180), (0, 365), (2, 145), (7, 145), (39, 154), (40, 145), (42, 154)]
    with fitz.open() as document:
        for index in range(45):
            page = document.new_page(width=612, height=792)
            shape = page.new_shape()
            shape.draw_rect(fitz.Rect(22, 22, 200, 80))
            shape.draw_rect(fitz.Rect(400, 300, 550, 330))
            shape.finish(color=(0, .5, .4), fill=(.9, 1, .95))
            shape.commit()
            page.insert_text((30, 50), "REFERENCE BRAND")
            page.insert_text((30, 740), "REFERENCE LAB FOOTER")
            page.insert_text((540, 770), f"Page {index + 1} of 45", fontsize=6)
            page.insert_text((50, 420), f"Body content page {index + 1}")
        document[0].insert_text((50, 240), "Current medication body")
        for title, (index, y) in zip(DEFAULT_HEADINGS, locations):
            document[index].insert_text((48, y), title, fontsize=12, color=(0, .5, .4))
        document.save(path)
    return path


def test_default_is_original_bytes(reference):
    assert render_reference_report(get_default_configuration(), reference) == reference.read_bytes()


def test_renaming_preserves_artwork(reference):
    configuration = get_default_configuration()
    configuration["sections"][0]["heading"] = "Custom <literal> medication heading"
    with fitz.open(stream=render_reference_report(configuration, reference), filetype="pdf") as document:
        assert len(document) == 45
        text = document[0].get_text()
        assert "Custom <literal> medication heading" in text
        assert "Current Patient Medications" not in text
        assert "REFERENCE BRAND" in text and "REFERENCE LAB FOOTER" in text
        with fitz.open(reference) as original:
            assert document[3].get_pixmap().samples == original[3].get_pixmap().samples


def test_reorder_preserves_content_and_page_numbers(reference):
    configuration = get_default_configuration()
    configuration["sections"].reverse()
    with fitz.open(stream=render_reference_report(configuration, reference), filetype="pdf") as document:
        assert len(document) == 46
        with fitz.open(reference) as original:
            header = fitz.Rect(0, 0, 612, 132)
            footer = fitz.Rect(0, 707, 612, 765)
            assert document[0].get_pixmap(clip=header).samples == original[42].get_pixmap(clip=header).samples
            assert document[0].get_pixmap(clip=footer).samples == original[42].get_pixmap(clip=footer).samples
        assert "Patient Information Card" in document[0].get_text(clip=fitz.Rect(0, 132, 612, 707))
        assert "Current Patient Medications" in document[-1].get_text(clip=fitz.Rect(0, 132, 612, 707))
        assert "Page 1 of 46" in document[0].get_text()
        assert "Page 46 of 46" in document[-1].get_text()
        text = "\n".join(p.get_text() for p in document)
        for index in range(45):
            assert f"Body content page {index + 1}" in text


def test_custom_header_footer(reference):
    configuration = get_default_configuration()
    configuration["header"].update(text="Custom report header", fontSize=20, italic=True)
    configuration["footer"].update(text="Custom report footer", fontSize=9, alignment="right")
    with fitz.open(stream=render_reference_report(configuration, reference), filetype="pdf") as document:
        for page in document:
            text = page.get_text()
            assert "Custom report header" in text and "Custom report footer" in text
            assert "REFERENCE BRAND" not in text and "REFERENCE LAB FOOTER" not in text
        with fitz.open(reference) as original:
            body = fitz.Rect(0, 132, 612, 707)
            assert document[0].get_pixmap(clip=body).samples == original[0].get_pixmap(clip=body).samples


def test_reference_api_and_missing_file(reference):
    settings = {"TESTING": True, "REPORT_REFERENCE_PATH": str(reference)}
    client = create_app(settings).test_client()
    saved = {"configuration": get_default_configuration(), "revision": 7}
    with patch("app.api.reports.load_current", return_value=saved):
        response = client.post("/api/reports")
        assert response.status_code == 200
        assert response.data == reference.read_bytes()
        assert response.headers["X-Report-Layout"] == "reference"
    client = create_app({**settings, "REPORT_REFERENCE_PATH": str(reference.parent / "missing.pdf")}).test_client()
    with patch("app.api.reports.load_current", return_value=saved):
        response = client.post("/api/reports")
        assert response.status_code == 503
        assert response.json["error"]["code"] == "reference_unavailable"


def test_invalid_source(tmp_path):
    path = tmp_path / "wrong.pdf"
    with fitz.open() as document:
        document.new_page()
        document.save(path)
    with pytest.raises(ReferenceReportError):
        render_reference_report(get_default_configuration(), path)


def test_empty_header_and_footer_keep_body(reference):
    configuration = get_default_configuration()
    configuration["header"]["text"] = ""
    configuration["footer"]["text"] = ""
    with fitz.open(stream=render_reference_report(configuration, reference), filetype="pdf") as document:
        assert len(document) == 45
        assert "REFERENCE BRAND" not in document[0].get_text()
        assert "REFERENCE LAB FOOTER" not in document[0].get_text()
        assert "Current Patient Medications" in document[0].get_text()
