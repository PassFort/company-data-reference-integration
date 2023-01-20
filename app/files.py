import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def static_file_path(*components):
    return os.path.join(PROJECT_ROOT, "static", *components)
