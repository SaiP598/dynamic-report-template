from copy import deepcopy
from io import BytesIO
from unittest.mock import patch

from pypdf import PdfReader
from sqlalchemy.exc import OperationalError

from app import create_app
from app.data.defaults import get_default_configuration
from app.data.report_content import get_report_content
from app.services.reports import render_report


def texts(pdf):
    return [page.extract_text() for page in PdfReader(BytesIO(pdf)).pages]


def test_order_headings_and_escaped_text():
    config = get_default_configuration()
    config["sections"].reverse()
    config["sections"][0]["heading"] = "Card <b>literal</b> & summary"
    config["header"].update(text="Header <b>plain</b>", alignment="right", italic=True)
    config["footer"].update(text="My footer", bold=True)
    output = texts(render_report(config))
    combined = "\n".join(output)
    assert "Card <b>literal</b> & summary" in combined
    assert combined.index("Card <b>literal</b>") < combined.index("Current Patient Medications")
    assert "DEMO-GENE" in combined
    for page in output:
        assert "Header <b>plain</b>" in page
        assert "My footer" in page
        assert "Demo Patient" in page
        assert "Page " in page


def test_multipage_table_and_long_decorations():
    config = get_default_configuration()
    config["header"].update(text="Long header " * 80, fontSize=36)
    config["footer"].update(text="Long footer " * 80, fontSize=36)
    content = get_report_content()
    row = content["sections"]["impacted-medications"]["rows"][0]
    content["sections"]["impacted-medications"]["rows"] = [
        dict(deepcopy(row), category=f"Category {n}") for n in range(100)]
    # A row larger than a page must split safely rather than raise LayoutError.
    content["sections"]["test-details"]["rows"][0]["phenotype"] = "Long result " * 1200
    output = texts(render_report(config, content))
    assert len(output) > 3
    combined = "\n".join(output)
    assert "Category 99" in combined
    assert "Patient Information Card" in combined
    assert sum("Drug Class" in p for p in output) > 1
    for page in output:
        assert "Long header" in page and "Long footer" in page


def test_report_endpoint_saved_snapshot_and_errors():
    client = create_app({"TESTING": True}).test_client()
    saved = {"configuration": get_default_configuration(), "revision": 12}
    saved["configuration"]["header"]["text"] = "Saved server header"
    with patch("app.api.reports.load_current", return_value=saved):
        response = client.post("/api/reports")
        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.headers["X-Template-Revision"] == "12"
        assert "attachment" in response.headers["Content-Disposition"]
        assert response.headers["Cache-Control"] == "no-store"
        assert "Saved server header" in texts(response.data)[0]
        assert client.post("/api/reports", json={"configuration": {}}).status_code == 400
    with patch("app.api.reports.load_current", side_effect=OperationalError("secret", {}, Exception())):
        response = client.post("/api/reports")
        assert response.status_code == 503
        assert "secret" not in response.get_data(as_text=True)


def test_blank_and_newline_heavy_decorations_fit():
    config = get_default_configuration()
    config["header"]["text"] = "\n" * 999
    config["footer"]["text"] = ""
    assert "Current Patient Medications" in "\n".join(texts(render_report(config)))


def test_format_only_layout_uses_placeholders_without_reference_reads():
    with patch("pathlib.Path.read_bytes", side_effect=AssertionError("Reference reads are forbidden")):
        pdf = render_report(get_default_configuration())
    reader = PdfReader(BytesIO(pdf))
    assert float(reader.pages[0].mediabox.width) == 612
    assert float(reader.pages[0].mediabox.height) == 792
    output = "\n".join(page.extract_text() for page in reader.pages)
    assert "<br/>" not in output
    assert "Proove Genomics, Inc." in output
    assert len(reader.pages[0].images) >= 1
    for label in ("PATIENT INFORMATION", "SPECIMEN DETAILS", "PROVIDER INFORMATION",
                  "Demo Patient", "Demo Laboratory", "SYNTHETIC DEMONSTRATION"):
        assert label in output
