"""Strict validation of the complete version-one layout payload."""
from copy import deepcopy
import re

from ..data.defaults import SECTION_IDS


class ConfigurationError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise ConfigurationError(message)


def _keys(value, keys, path):
    _require(type(value) is dict, f"{path} must be an object.")
    _require(set(value) == set(keys), f"{path} must contain exactly: {', '.join(keys)}.")


def validate_configuration(value):
    _keys(value, ("schemaVersion", "sections", "header", "footer"), "configuration")
    _require(type(value["schemaVersion"]) is int and value["schemaVersion"] == 1,
             "schemaVersion must be 1.")
    sections = value["sections"]
    _require(type(sections) is list and len(sections) == len(SECTION_IDS),
             "sections must contain all seven sections exactly once.")
    ids = []
    for index, section in enumerate(sections):
        path = f"sections[{index}]"
        _keys(section, ("id", "heading"), path)
        _require(type(section["id"]) is str and section["id"] in SECTION_IDS,
                 f"{path}.id must be a known section ID.")
        ids.append(section["id"])
        heading = section["heading"]
        _require(type(heading) is str and bool(heading.strip()) and len(heading) <= 120,
                 f"{path}.heading must be nonblank text of at most 120 characters.")
    _require(len(set(ids)) == len(SECTION_IDS), "Each section ID must appear exactly once.")
    for path in ("header", "footer"):
        formatting = value[path]
        _keys(formatting, ("text", "alignment", "fontSize", "bold", "italic", "color"), path)
        _require(type(formatting["text"]) is str and len(formatting["text"]) <= 1000,
                 f"{path}.text must be text of at most 1000 characters.")
        _require(type(formatting["alignment"]) is str and
                 formatting["alignment"] in ("left", "center", "right"),
                 f"{path}.alignment must be left, center, or right.")
        _require(type(formatting["fontSize"]) is int and 6 <= formatting["fontSize"] <= 36,
                 f"{path}.fontSize must be an integer from 6 to 36.")
        for flag in ("bold", "italic"):
            _require(type(formatting[flag]) is bool, f"{path}.{flag} must be a boolean.")
        _require(type(formatting["color"]) is str and
                 re.fullmatch(r"#[0-9a-fA-F]{6}", formatting["color"]) is not None,
                 f"{path}.color must be a six-digit hex color.")
    return deepcopy(value)
