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
               "italic": False, "color": "#ffffff"},
    "footer": {"text": "Demo Laboratory\nExample laboratory information\n"
                       "Synthetic report - not for clinical use\nExample address | example.invalid",
               "alignment": "left", "fontSize": 6, "bold": False,
               "italic": False, "color": "#555555"},
})


def get_default_configuration():
    """Return an independent configuration; the baseline is never persisted over."""
    return json.loads(_DEFAULT_JSON)
