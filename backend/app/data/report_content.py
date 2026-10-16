"""Synthetic structural fixtures, not clinical recommendations or patient records."""
from copy import deepcopy

_REPORT = {
    "patient": {"name": "Demo Patient", "dateOfBirth": "1980-01-01", "sex": "Unspecified"},
    "specimen": {"sampleId": "DEMO-001", "type": "Demonstration", "reportDate": "2026-10-16"},
    "provider": {"name": "Demo Provider", "facility": "Demo Laboratory"},
    "sections": {
        "current-medications": {
            "paragraphs": ["Synthetic medication information for report layout demonstration."],
            "medications": ["Example medication A"], "unrecognized": [], "outsideScope": [],
        },
        "risk-management": {"items": [
            {"title": "Example risk assessment", "category": "standard",
             "summary": "Synthetic finding", "details": "Demonstration content only."},
        ]},
        "impacted-medications": {
            "columns": ["Category", "Drug Class", "Standard Precautions", "Use with Caution", "Consider Alternatives"],
            "rows": [{"category": "Example category", "drugClass": "Example class",
                      "standard": ["Example medication A"], "caution": ["Example medication B"],
                      "alternatives": ["Example medication C"]}],
        },
        "dosing-guidance": {"items": [
            {"medication": "Example medication B", "evidence": "DEMO",
             "finding": "Synthetic finding", "guidance": "Placeholder for supplied report content; no dosing advice."},
        ]},
        "legend": {"items": [
            {"category": "standard", "label": "Standard Precautions", "color": "#d4eadb"},
            {"category": "caution", "label": "Use with Caution", "color": "#f6e7d7"},
            {"category": "alternatives", "label": "Consider Alternatives", "color": "#f3d8dc"},
        ], "evidenceLevels": ["STRONG", "MODERATE", "WEAK"]},
        "test-details": {"columns": ["Gene", "Genotype", "Phenotype"],
                         "rows": [{"gene": "DEMO-GENE", "genotype": "Example", "phenotype": "Synthetic result"}]},
        "patient-card": {"paragraphs": ["Demonstration summary card for Demo Patient."],
                         "rows": [{"gene": "DEMO-GENE", "genotype": "Example", "phenotype": "Synthetic result"}]},
    },
}


def get_report_content():
    """Layout preferences never mutate the source content."""
    return deepcopy(_REPORT)
