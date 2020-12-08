import json


def load_file(path):
    with open(f"demo_data/{path}") as f:
        data = json.load(f)
    return data


demo_create_response = {
    "CaseID": 1606134468911,
    "RequestDate": "2020-11-23T12:27:48.911789Z",
    "ResponseReady": False
}

demo_poll_success_response = {
    "CaseID": 1606134578911,
    "RequestDate": "2020-11-23T12:29:37.622710Z",
    "ResponseReady": True
}
