from os import path


def read_demo_file(name: str) -> str:
    with open(path.join(path.dirname(__file__), name)) as file:
        return file.read()


MATCH_RESPONSE = read_demo_file('match.xml')
NOMATCH_RESPONSE = read_demo_file('nomatch.xml')
