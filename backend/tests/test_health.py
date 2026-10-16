from app import create_app


def test_api_health_and_json_not_found():
    client = create_app({"TESTING": True}).test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    missing = client.get("/api/unknown")
    assert missing.status_code == 404
    assert "error" in missing.json
