"""Versioned baseline. Only fresh copies are exposed to callers."""
import json

SECTION_IDS = (
    "current-medications", "risk-management", "impacted-medications",
    "dosing-guidance", "legend", "test-details", "patient-card",
)
DEFAULT_HEADINGS = (
    "Current Patient Medications", "Risk Management", "Potentially Impacted Medications",
    "Dosing Guidance", "Legend", "Test Details", "Patient Information Card",
)

# Serialized storage prevents nested mutable objects from becoming shared state.
_DEFAULT_JSON = json.dumps({
    "schemaVersion": 1,
    "sections": [dict(id=id_, heading=heading)
                 for id_, heading in zip(SECTION_IDS, DEFAULT_HEADINGS)],
    "header": {"text": "Proove Drug Metabolism (Reprocessing)",
               "alignment": "center", "fontSize": 14, "bold": True,
               "italic": False, "color": "#009688"},
    "footer": {"text": "Labarium Diagnostic Systems, Inc.\n"
                       "InfinitiLabs, Inc.(\"InfinitiLabs\") is an agent of Labarium Diagnostic Systems, Inc.\n"
                       "425 Grand Boulevard, Suite 206, Miramar Beach, Florida, USA 32550\n"
                       "www.Labarium.com\n"
                       "Laboratory Performing Test: InfinitiLabs, Inc\n"
                       "Laboratory Director: Dr. Barroso-Vicens, MD\n"
                       "6015 Benjamin Road, Suite 315, Tampa, FL 33634\n"
                       "Phone: 813-886-2616, Fax: 813-886-2735 | CLIA:10D2020310",
               "alignment": "left", "fontSize": 6, "bold": False,
               "italic": False, "color": "#555555"},
})


def get_default_configuration():
    """Return an independent configuration; the baseline is never persisted over."""
    return json.loads(_DEFAULT_JSON)
