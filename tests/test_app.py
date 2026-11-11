import json

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "DATA_FILE": tmp_path / "submissions.json"})
    return app.test_client()


def valid_payload():
    return {"name": "Ayesha Khan", "registration_number": "FA22-BCS-001",
            "assignment_title": "DevOps Lab", "submission_url": "https://example.com/submission"}


def test_valid_submission_is_saved_and_listed(client, tmp_path):
    response = client.post("/submit", data=valid_payload(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Ayesha Khan" in response.data
    assert json.loads((tmp_path / "submissions.json").read_text())[0]["registration_number"] == "FA22-BCS-001"


def test_missing_registration_number_is_rejected(client, tmp_path):
    payload = valid_payload()
    payload["registration_number"] = ""
    response = client.post("/submit", data=payload)
    assert response.status_code == 400
    assert b"Registration number is required." in response.data
    assert not (tmp_path / "submissions.json").exists()


def test_invalid_submission_url_is_rejected(client, tmp_path):
    payload = valid_payload()
    payload["submission_url"] = "not-a-url"
    response = client.post("/submit", data=payload)
    assert response.status_code == 400
    assert b"Submission URL must be a valid" in response.data
    assert not (tmp_path / "submissions.json").exists()
