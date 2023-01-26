import base64
import os
import time
import urllib.parse
from email.utils import formatdate
from uuid import uuid4


def test_run_check_protected(session, auth):
    # Should require authentication
    r = session.post("http://app/monitored-polling/checks", json={})
    assert r.status_code == 401

    # Should require correct key
    bad_key = os.urandom(256)
    r = session.post(
        "http://app/monitored-polling/checks", json={}, auth=auth(key=bad_key)
    )
    assert r.status_code == 401

    # Should require '(request-target)' *and* 'date' headers to be signed
    r = session.post(
        "http://app/monitored-polling/checks", json={}, auth=auth(headers=["date"])
    )
    assert r.status_code == 401

    # Should require 'date' header to be recent
    old_date = formatdate(time.time() - 120)
    r = session.post(
        "http://app/monitored-polling/checks",
        json={},
        headers={"date": old_date},
        auth=auth(),
    )
    assert r.status_code == 401

    # Should require digest to be correct
    bad_digest = base64.b64encode(os.urandom(256)).decode()
    r = session.post(
        "http://app/monitored-polling/checks",
        json={},
        headers={"digest": f"SHA-256={bad_digest}"},
        auth=auth(),
    )
    assert r.status_code == 401


def test_run_check_smoke(session, auth):
    # two parts to every polling check: initiate check...
    check_response = session.post(
        "http://app/monitored-polling/checks",
        json={
            "id": str(uuid4()),
            "check_input": {
                "entity_type": "COMPANY",
                "metadata": {
                    "name": "PASSFORT LIMITED",
                    "number": "09565115",
                    "country_of_incorporation": "GBR",
                },
            },
            "commercial_relationship": "DIRECT",
            "provider_config": {},
            "demo_result": "NO_DATA",
        },
        auth=auth(),
    )

    assert check_response.status_code == 200
    assert check_response.headers["content-type"] == "application/json"
    check_result = check_response.json()
    assert check_result["errors"] == []
    assert "reference" in check_result
    assert check_result["reference"] != ""
    assert check_result["provider_id"] == "b4165f9c-8d21-11ed-90f6-4f528b1df65f"

    # ...then poll for final result
    check_reference = check_result["reference"]
    check_id = str(uuid4())
    poll_response = session.post(
        f"http://app/monitored-polling/checks/{check_id}/poll",
        json={
            "id": check_id,
            "reference": check_reference,
            "custom_data": {},
            "commercial_relationship": "DIRECT",
            "provider_config": {},
        },
        auth=auth(),
    )

    assert poll_response.status_code == 200
    assert poll_response.headers["content-type"] == "application/json"
    poll_result = poll_response.json()
    assert "pending" in poll_result
    assert "errors" in poll_result
    assert not poll_result["pending"]
    assert poll_result["errors"] == []
    assert poll_result["charges"] == []


def test_run_check_unsupported_demo_result(session, auth):
    check_response = session.post(
        "http://app/monitored-polling/checks",
        json={
            "id": str(uuid4()),
            "check_input": {
                "entity_type": "COMPANY",
                "metadata": {
                    "name": "PASSFORT LIMITED",
                    "number": "09565115",
                    "country_of_incorporation": "GBR",
                },
            },
            "commercial_relationship": "DIRECT",
            "provider_config": {},
            "demo_result": "NOT_A_REAL_DEMO_RESULT",
        },
        auth=auth(),
    )

    assert check_response.status_code == 200
    assert check_response.headers["content-type"] == "application/json"
    check_result = check_response.json()
    assert "reference" in check_result

    check_reference = check_result["reference"]
    check_id = str(uuid4())
    poll_response = session.post(
        f"http://app/monitored-polling/checks/{check_id}/poll",
        json={
            "id": check_id,
            "reference": check_reference,
            "custom_data": {},
            "commercial_relationship": "DIRECT",
            "provider_config": {},
        },
        auth=auth(),
    )

    assert poll_response.status_code == 200
    assert poll_response.headers["content-type"] == "application/json"
    poll_result = poll_response.json()
    assert "pending" in poll_result
    assert "errors" in poll_result
    assert "charges" in poll_result
    assert not poll_result["pending"]
    assert poll_result["errors"] == [
        {
            "type": "UNSUPPORTED_DEMO_RESULT",
            "message": "Demo result is not supported.",
        }
    ]
    assert poll_result["charges"] == []


def test_resold_check_has_valid_charges(session, auth):
    check_response = session.post(
        "http://app/monitored-polling/checks",
        json={
            "id": str(uuid4()),
            "check_input": {
                "entity_type": "COMPANY",
                "metadata": {
                    "name": "PASSFORT LIMITED",
                    "number": "09565115",
                    "country_of_incorporation": "GBR",
                },
            },
            "commercial_relationship": "PASSFORT",
            "provider_config": {},
            "demo_result": "ALL_DATA",
        },
        auth=auth(),
    )

    assert check_response.status_code == 200
    assert check_response.headers["content-type"] == "application/json"
    check_result = check_response.json()
    assert check_result["errors"] == []
    assert "reference" in check_result
    assert check_result["reference"] != ""
    assert check_result["provider_id"] == "b4165f9c-8d21-11ed-90f6-4f528b1df65f"

    # ...then poll for final result
    check_reference = check_result["reference"]
    check_id = str(uuid4())
    poll_response = session.post(
        f"http://app/monitored-polling/checks/{check_id}/poll",
        json={
            "id": check_id,
            "reference": check_reference,
            "custom_data": {},
            "commercial_relationship": "PASSFORT",
            "provider_config": {},
        },
        auth=auth(),
    )

    assert poll_response.status_code == 200
    assert poll_response.headers["content-type"] == "application/json"
    poll_result = poll_response.json()
    assert "pending" in poll_result
    assert "errors" in poll_result
    assert "charges" in poll_result
    assert not poll_result["pending"]
    assert poll_result["errors"] == []
    assert poll_result["charges"] == [
        {"amount": 100, "reference": "DUMMY REFERENCE"},
        {"amount": 50, "sku": "NORMAL"},
    ]


def test_cannot_use_invalid_poll_reference(session, auth):
    invalid_reference = urllib.parse.quote("notareference")

    response = session.post(
        f"http://app/monitored-polling/monitored_checks/{invalid_reference}/poll",
        json={
            "reference": invalid_reference,
            "commercial_relationship": "DIRECT",
            "provider_config": {},
        },
        auth=auth(),
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert "errors" in result
    assert result["errors"] == [
        [{"message": "Reference must be a valid UUID", "type": "INVALID_INPUT"}],
    ]


def test_cannot_use_invalid_update_reference(session, auth):
    invalid_reference = urllib.parse.quote("notareference")

    response = session.post(
        f"http://app/monitored-polling/monitored_checks/{invalid_reference}/_update",
        json={},
        auth=auth(),
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    result = response.json()
    assert "errors" in result
    assert result["errors"] == [
        [{"message": "Reference must be a valid UUID", "type": "INVALID_INPUT"}],
    ]
