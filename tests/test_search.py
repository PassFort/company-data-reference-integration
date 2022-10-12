import base64
import os
import time

from email.utils import formatdate


def test_run_search_protected(session, auth):
    # Should require authentication
    r = session.post('http://app/search', json={})
    assert r.status_code == 401

    # Should require correct key
    bad_key = os.urandom(256)
    r = session.post('http://app/search', json={}, auth=auth(key=bad_key))
    assert r.status_code == 401

    # Should require '(request-target)' *and* 'date' headers to be signed
    r = session.post('http://app/search', json={}, auth=auth(headers=['date']))
    assert r.status_code == 401

    # Should require 'date' header to be recent
    old_date = formatdate(time.time() - 120)
    r = session.post('http://app/search', json={}, headers={'date': old_date}, auth=auth())
    assert r.status_code == 401

    # Should require digest to be correct
    bad_digest = base64.b64encode(os.urandom(256)).decode()
    r = session.post('http://app/search', json={}, headers={'digest': f'SHA-256={bad_digest}'}, auth=auth())
    assert r.status_code == 401


def test_run_demo_search(session, auth):
    import json

    r = session.post('http://app/search', json={
        "demo_result": "MANY_HITS",
        "commercial_relationship": "DIRECT",
        "search_input": {
            "query": "Passfort",
            "country_of_incorporation": "GBR",
            "state_of_incorporation": ""
        },
        "provider_config": {},
    }, auth=auth())
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/json'

    res = r.json()

    assert res['errors'] == []

    with open(os.path.join(os.path.dirname(__file__), "../static/demo_results/MANY_HITS.json"), 'r') as file:
        demo_data = json.loads(file.read())

    # Make sure the response is JSON equivalent to the MANY_HITS data
    assert json.dumps(res["search_output"], sort_keys=True, indent=2) ==\
           json.dumps(demo_data["search_output"], sort_keys=True, indent=2)

    # Also do a sanity check to make sure that the first company has all the allowed fields
    # so that our tests are actually useful
    assert frozenset([
        "name",
        "number_label",
        "number",
        "country_of_incorporation",
        "status",
        "provider_reference",
        "addresses",
        "contact",
        "incorporation_date",
        "tax_ids",
        "structure_type",
        "lei",
    ]) == frozenset(res["search_output"][0].keys())
