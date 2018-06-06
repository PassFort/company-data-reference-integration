
class BasicResponse:
    def __init__(self, data):
        self.data = data


def create_response_from_file(file_name):
    with open(file_name, 'rb') as f:
        return BasicResponse(f.read())


def get_json_from_file(file_name):
    import json
    with open(file_name, 'rb') as f:
        return json.loads(f.read())
