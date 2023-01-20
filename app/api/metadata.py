from flask import Blueprint, send_file

from app.files import static_file_path

metadata_api = Blueprint("metadata", __name__)


@metadata_api.route("/")
def index():
    return send_file(static_file_path("metadata.json"), max_age=-1)
