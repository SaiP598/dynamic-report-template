"""API contract tests, using a disposable schema in a dedicated test database."""
from copy import deepcopy
import os
from unittest.mock import patch

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import create_app
from app.data.defaults import get_default_configuration
from app.extensions import db


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


def test_default_and_invalid_json(client):
    response = client.get("/api/templates/default")
    assert response.json["configuration"] == get_default_configuration()
    assert response.json["revision"] == 0
    for kwargs, status in [({"data": "{", "content_type": "application/json"}, 400),
                           ({"data": "text", "content_type": "text/plain"}, 415),
                           ({"json": []}, 400), ({"json": {"schemaVersion": 1}}, 400)]:
        response = client.put("/api/templates/current", **kwargs)
        assert response.status_code == status
        assert "error" in response.json
    assert client.post("/api/templates/current/restore", json={}).status_code == 400


@pytest.mark.parametrize("mutation", [
    lambda c: c.update(schemaVersion=True),
    lambda c: c.update(extra="unknown"),
    lambda c: c["sections"].pop(),
    lambda c: c["sections"][0].update(id="unknown"),
    lambda c: c["sections"][0].update(id=c["sections"][1]["id"]),
    lambda c: c["sections"][0].update(heading="   "),
    lambda c: c["sections"][0].update(heading="x" * 121),
    lambda c: c["sections"][0].update(extra=1),
    lambda c: c["header"].update(fontSize=True),
    lambda c: c["header"].update(fontSize=37),
    lambda c: c["header"].update(fontSize=5),
    lambda c: c["header"].update(bold="true"),
    lambda c: c["footer"].update(color="red"),
    lambda c: c["footer"].update(alignment=[]),
    lambda c: c["footer"].update(text="x" * 1001),
])
def test_invalid_payload_never_writes(client, mutation):
    payload = get_default_configuration()
    mutation(payload)
    with patch("app.api.templates.save_configuration") as save:
        response = client.put("/api/templates/current", json=payload)
    assert response.status_code == 400
    assert response.json["error"]["code"] == "validation_error"
    save.assert_not_called()


def test_database_errors_are_sanitized_and_rolled_back(client):
    for route, method, kwargs, target in [
        ("/api/templates/current", "get", {}, "load_current"),
        ("/api/templates/current", "put", {"json": get_default_configuration()}, "save_configuration"),
        ("/api/templates/current/restore", "post", {}, "save_configuration"),
    ]:
        with patch("app.api.templates." + target, side_effect=OperationalError("secret", {}, Exception("password"))), patch("app.api.templates.db.session.rollback") as rollback:
            response = getattr(client, method)(route, **kwargs)
            assert response.status_code == 503
            assert "secret" not in response.get_data(as_text=True)
            assert "password" not in response.get_data(as_text=True)
            rollback.assert_called_once()


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Requires dedicated PostgreSQL test database")
def test_saved_configuration_survives_new_app_and_restore():
    url = os.environ["TEST_DATABASE_URL"]
    # Schema isolation allows real commits without touching another test's saved row.
    import uuid
    schema = "api_test_" + uuid.uuid4().hex
    admin_app = create_app({"TESTING": True, "DATABASE_URL": url})
    with admin_app.app_context():
        db.session.execute(text(f'CREATE SCHEMA "{schema}"'))
        db.session.commit()
    options = {"connect_args": {"options": f"-csearch_path={schema}"}}
    settings = {"TESTING": True, "DATABASE_URL": url, "SQLALCHEMY_ENGINE_OPTIONS": options}
    first = create_app(settings)
    try:
        with first.app_context():
            from flask_migrate import upgrade
            upgrade()
        client = first.test_client()
        baseline = client.get("/api/templates/default").json
        assert client.get("/api/templates/current").json == baseline
        payload = deepcopy(baseline["configuration"])
        payload["sections"].reverse()
        payload["sections"][0]["heading"] = "Custom heading"
        payload["header"].update(text="Custom header", bold=False, italic=True, fontSize=20)
        payload["footer"].update(text="", alignment="right", color="#123aBC")
        saved = client.put("/api/templates/current", json=payload)
        assert saved.status_code == 200
        assert saved.json["configuration"] == payload
        assert saved.json["revision"] == 1
        assert saved.json["updatedAt"] is not None
        assert saved.json["isDefault"] is False
        from io import BytesIO
        from pypdf import PdfReader
        pdf = client.post("/api/reports")
        assert pdf.status_code == 200
        pdf_text = "\n".join(page.extract_text() for page in PdfReader(BytesIO(pdf.data)).pages)
        assert "Custom heading" in pdf_text and "Custom header" in pdf_text
        assert pdf.headers["X-Template-Revision"] == "1"
        second = create_app(settings).test_client()
        assert second.get("/api/templates/current").json == saved.json
        invalid = deepcopy(payload)
        invalid["sections"] = []
        assert second.put("/api/templates/current", json=invalid).status_code == 400
        assert second.get("/api/templates/current").json == saved.json
        assert second.put("/api/templates/current", json=payload).json["revision"] == 2
        restored = second.post("/api/templates/current/restore")
        assert restored.status_code == 200
        assert restored.json["configuration"] == baseline["configuration"]
        assert restored.json["revision"] == 3
        assert restored.json["isDefault"] is True
        pdf = second.post("/api/reports")
        pdf_text = "\n".join(page.extract_text() for page in PdfReader(BytesIO(pdf.data)).pages)
        assert "Custom heading" not in pdf_text
        assert "Current Patient Medications" in pdf_text
        assert create_app(settings).test_client().get("/api/templates/current").json == restored.json
        assert client.get("/api/templates/default").json == baseline
    finally:
        with admin_app.app_context():
            db.session.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            db.session.commit()
