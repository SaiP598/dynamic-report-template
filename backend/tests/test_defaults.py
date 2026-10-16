from app.data.defaults import SECTION_IDS, get_default_configuration
from app.data.report_content import get_report_content


def test_defaults_and_content_are_independent_copies():
    configuration = get_default_configuration()
    original = get_default_configuration()
    assert tuple(section["id"] for section in configuration["sections"]) == SECTION_IDS
    assert set(get_report_content()["sections"]) == set(SECTION_IDS)
    configuration["sections"].reverse()
    configuration["sections"][0]["heading"] = "Changed"
    configuration["header"]["text"] = "Changed"
    assert get_default_configuration() == original
    content = get_report_content()
    content["sections"]["test-details"]["rows"].clear()
    assert get_report_content()["sections"]["test-details"]["rows"]
